from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account
from accounts.serializers import AccountSerializer


class AccountAPIs(APIView):
    """
        GET: list user accounts | POST: add an account | PUT/PATCH: update balance
        Update API might be used to add money other than through other customer transfers.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """
        If requesting user is a superuser, a list of all accounts are sent, else accounts of the user

        :param format: optional, data format
        :param request: HTTP request type django class obj
        :return:
            - dict with following keys:
                - success: True/False based on request data. If True, API call completed successfully
                - err_msg: Message informing caller about the reason of failure, if success = False
                - data: list of accounts
            - status: standard HTTP status code
        """
        if request.user.is_superuser:
            user_acc_objs = Account.active_objects.all()
        else:
            user_acc_objs = Account.active_objects.filter(owner=request.user)  # may have multiple accounts

        serializer = self.serializer_class(user_acc_objs, many=True)
        return Response(
                {
                    "data": serializer.data,
                    "success": True
                },
                status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """
        Add account for a user.

        :param format: optional, data format
        :param request: HTTP request type django class obj
        :return:
            - dict with following keys:
                - success: True/False based on request data. If True, data saved successfully
                - err_msg: Message informing caller about the reason of failure, if success = False
                - data: Details of the account saved, if success = True
            - status: standard HTTP status code
        """
        req_data = request.data
        req_data['owner'] = request.user
        if not req_data.get('currency'):
            req_data['currency'] = "PHP"
        req_data["balance"] = 0.0  # during account creation balance should be 0

        serializer = self.serializer_class(data=req_data)
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

    def put(self, request, pk, format=None):
        """
        Update user account balance. Only Superuser is authorized.

        :param pk: primary key of the row to be updated
        :param format: optional, data format
        :param request: HTTP request type django class obj
        :return:
            - dict with following keys:
                - success: True/False based on request data. If True, data saved successfully
                - err_msg: Message informing caller about the reason of failure, if success = False
                - data: Details of the account saved, if success = True
            - status: standard HTTP status code
        """

        if not request.user.is_superuser:  # authorization
            return Response(
                {
                    "err_msg": "Only a superuser may change balance without transfers.",
                    "success": False
                },
                status=status.HTTP_400_BAD_REQUEST)
        try:
            acc_obj = Account.active_objects.get(pk=pk, owner=request.user)  # authorization check
        except Account.DoesNotExist:
            return Response(
                {
                    "err_msg": "Entry with given ID not found or User not owner.",
                    "success": False
                },
                status=status.HTTP_400_BAD_REQUEST)

        if not request.data.get('balance'):
            return Response(
                {
                    "err_msg": "New balance to update account not received.",
                    "success": False
                },
                status=status.HTTP_400_BAD_REQUEST)

        # validate 'new_balance' to be a valid float
        try:
            new_balance = float(request.data['balance'])
        except ValueError:
            return Response(
                {
                    "err_msg": "New balance should be a valid float number.",
                    "success": False
                },
                status=status.HTTP_400_BAD_REQUEST)

        # only balance updating supported for the scope of this project. Change in currency not.
        serializer = self.serializer_class(acc_obj, data={"balance": new_balance})
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
