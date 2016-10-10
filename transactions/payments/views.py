from __future__ import print_function

from django.db import transaction as db_transaction

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account
from payments.serializers import TransactionSerializer

exec("from django.db.models import Q")  # as used inside eval()
exec("from payments.models import Transaction")  # as used inside eval()
from proj_utils import CURRENCY_CONVERSION


class PaymentApis(APIView):
    """
        GET: To list payments related to a user | POST: add a payment(do a transfer)
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        GET request handler, returns a list of rows from the 'Transaction' table.
        Represents the API used to get list of payments received or sent by the request user.

        :param request: HTTP request type django class obj
        :return:
            - dict with following keys:
                - success: True/False based on request data. If True, API call completed successfully
                - err_msg: Message informing caller about the reason of failure, if success = False
                - data: list of payments
            - status: standard HTTP status code
        """
        user_acc_objs = Account.active_objects.filter(owner=request.user)  # may have multiple accounts
        if not user_acc_objs:
            return Response(
                {
                    "data": [],
                    "success": True
                },
                status=status.HTTP_200_OK)

        # form ORM query string for single DB hit that would result in performance gain
        payment_objs = []
        q = "payment_objs = Transaction.active_objects.filter("
        for acc_id in user_acc_objs.values('id'):
            q += 'Q(from_account_id=%s)|' % acc_id
            q += 'Q(to_account_id=%s)|' % acc_id
        q[-1] = ')'  # replace last '|'
        eval(q)

        serializer = self.serializer_class(payment_objs, many=True)
        return Response(
                {
                    "data": serializer.data,
                    "success": True
                },
                status=status.HTTP_200_OK)

    def post(self, request):
        """
        POST request handler, creates an entry/row in the 'Transaction' table.
        Represents the API used to make a payment.

        :param request: HTTP request type django class obj
        :return:
            - dict with following keys:
                - success: True/False based on request data. If True, transaction completed successfully
                - err_msg: Message informing caller about the reason of failure, if success = False
                - data: Details of the transaction saved, if success = True
            - status: standard HTTP status code
        """
        req_data = request.data

        # validate request data for mandatory fields
        if not all([req_data.get('from_account_id'), req_data.get('to_account_id'), req_data.get('amount')]):
            return Response(
                {
                    "err_msg": "Request lacks a mandatory fields('from_account_id', 'to_account_id', 'amount').",
                    "success": False
                },
                status=status.HTTP_400_BAD_REQUEST)

        # validate 'amount' to be a valid float
        try:
            debit_amount = float(req_data['amount'])
        except ValueError:
            return Response(
                {
                    "err_msg": "'amount' should be a valid float number.",
                    "success": False
                },
                status=status.HTTP_400_BAD_REQUEST)

        to_acc_id = req_data['to_account_id']
        from_acc_id = req_data['from_account_id']

        sender_account_objs = Account.active_objects.filter(owner=request.user)

        if not sender_account_objs or from_acc_id not in sender_account_objs.values('id'):
            return Response(
                {
                    "err_msg": "Account to be debited for transaction not owned by requested user.",
                    "success": False
                },
                status=status.HTTP_400_BAD_REQUEST)

        # 'to' and 'from' account IDs should not be same
        if to_acc_id == from_acc_id:
            return Response(
                {
                    "err_msg": "To and From accounts should not be same.",
                    "success": False
                },
                status=status.HTTP_400_BAD_REQUEST)

        # validate 'to' account is valid and active
        try:
            receiver_acc_obj = Account.active_objects.get(id=to_acc_id)
        except Account.DoesNotExist:
            return Response(
                {
                    "err_msg": "Account to receive payment(to_account_id) is Invalid.",
                    "success": False
                },
                status=status.HTTP_400_BAD_REQUEST)

        # validate sync with receivers currency
        senders_acc_obj = sender_account_objs.filter(id=from_acc_id)
        # All transfers are assumed to be happening in senders currency.
        # In case receivers account currency is diff, credit_amount != amount, conversion will be required
        if senders_acc_obj.currency != receiver_acc_obj.currency:
            if not CURRENCY_CONVERSION.get(senders_acc_obj.currency) \
                    or not CURRENCY_CONVERSION.get(receiver_acc_obj.currency):
                return Response(
                    {
                        "err_msg": "Users currency currently not supported for transfers.",
                        "success": False
                    },
                    status=status.HTTP_400_BAD_REQUEST)

            credit_amount = (
                                debit_amount/CURRENCY_CONVERSION[senders_acc_obj.currency]  # to BTC
                            ) * CURRENCY_CONVERSION[receiver_acc_obj.currency]
        else:
            credit_amount = debit_amount

        # validate balance in 'from' account to be sufficient
        if not float(senders_acc_obj.balance) >= debit_amount:
            return Response(
                {
                    "err_msg": "Balance insufficient to complete transaction.",
                    "success": False
                },
                status=status.HTTP_400_BAD_REQUEST)

        # #### Coming here means all validations are passed and transaction can go through
        with db_transaction.atomic():  # all database commits under this scope happen or none(rollback)
            # reduce balance from senders account
            senders_acc_obj.balance -= debit_amount
            senders_acc_obj.save()

            # credit amount to receiver account
            receiver_acc_obj.balance += credit_amount
            receiver_acc_obj.save()

            # save transaction data to table
            data_dict_to_save = {
                "is_active": True,  # at the time of payment, transaction should be active by default
                "amount": debit_amount,
                "from_account_id": from_acc_id,
                "to_account_id": to_acc_id,
            }
            serializer = self.serializer_class(data=data_dict_to_save)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "data": serializer.data,
                        "success": True
                    },
                    status=status.HTTP_201_CREATED)
            return Response(
                    {
                        "err_msg": serializer.errors,
                        "success": False
                    },
                    status=status.HTTP_400_BAD_REQUEST)

