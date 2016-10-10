import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from oauth2_provider.models import Application, AccessToken
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import Account
from proj_utils import CURRENCY_CONVERSION


class AccountsTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.sender_user = User.objects.create_user("sender_user", "sender_user@user.com", "sender_pass")
        self.receiver_user = User.objects.create_user("receiver_user", "receiver_user@user.com", "receiver_pass")
        self.admin_user = User.objects.create_superuser("admin_user", "admin_user@user.com", "admin_pass")

        self.application = Application(
            name="Test Application",
            redirect_uris="http://localhost",
            user=self.sender_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.application.save()

        self.sender_token = AccessToken.objects.create(
            user=self.sender_user, token='sender_token',
            application=self.application, scope='read write',
            expires=timezone.now() + datetime.timedelta(days=1)
        )
        self.receiver_token = AccessToken.objects.create(
            user=self.receiver_user, token='receiver_token',
            application=self.application, scope='read write',
            expires=timezone.now() + datetime.timedelta(days=1)
        )
        self.admin_token = AccessToken.objects.create(
            user=self.admin_user, token='admin_token',
            application=self.application, scope='read write',
            expires=timezone.now() + datetime.timedelta(days=1)
        )

    def test_transaction(self):
        # add sender account to ensure one exists
        url = reverse('accounts_list_add')
        sender_currency = "BTC"
        data = {"currency": sender_currency}  # non default currency
        response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION="Bearer %s" % self.sender_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # add receiver account to ensure one exists
        response = self.client.post(url, {}, format='json', HTTP_AUTHORIZATION="Bearer %s" % self.receiver_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        from_acc = Account.active_objects.filter(owner=self.sender_user)[0]
        from_balance = 11.11
        to_acc = Account.active_objects.filter(owner=self.receiver_user)[0]
        to_balance = 0

        # add amount to sender account
        url += str(from_acc.id) + "/"
        data = {"balance": from_balance}
        response = self.client.put(url, data, format='json', HTTP_AUTHORIZATION="Bearer %s" % self.admin_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # transfer amount
        amount = 1.01
        transfer_api = reverse('payment_add_list')
        data = {
            "to_account_id": to_acc.id,
            "from_account_id": from_acc.id,
            "amount": amount,
        }
        response = self.client.post(transfer_api, data, format='json', HTTP_AUTHORIZATION="Bearer %s" % self.sender_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check for correct balances post transfer
        from_acc_post_save = Account.active_objects.get(id=from_acc.id)
        to_acc_post_save = Account.active_objects.get(id=to_acc.id)
        receiver_currency_amount = (amount/CURRENCY_CONVERSION[sender_currency]) * CURRENCY_CONVERSION[to_acc.currency]
        self.assertEqual(from_balance - amount, float(from_acc_post_save.balance))
        self.assertEqual(to_balance + receiver_currency_amount, float(to_acc_post_save.balance))

        # coming here means unit test is passed
        # all tests that follow in this method are designed to fail the transfer process

        # non float amount
        amount = "fqf"
        data = {
            "to_account_id": to_acc.id,
            "from_account_id": from_acc.id,
            "amount": amount,
        }
        response = self.client.post(transfer_api, data, format='json',
                                    HTTP_AUTHORIZATION="Bearer %s" % self.sender_token)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

        # same account
        amount = 1
        data = {
            "to_account_id": to_acc.id,
            "from_account_id": to_acc.id,
            "amount": amount,
        }
        response = self.client.post(transfer_api, data, format='json',
                                    HTTP_AUTHORIZATION="Bearer %s" % self.sender_token)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

        # insufficient balance
        amount = 11111
        data = {
            "to_account_id": to_acc.id,
            "from_account_id": from_acc.id,
            "amount": amount,
        }
        response = self.client.post(transfer_api, data, format='json',
                                    HTTP_AUTHORIZATION="Bearer %s" % self.sender_token)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_acc_list(self):
        url = reverse('accounts_list_add')
        response = self.client.get(url, {}, format='json', HTTP_AUTHORIZATION="Bearer %s" % self.sender_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_list(self):
        url = reverse('payment_add_list')
        response = self.client.get(url, {}, format='json', HTTP_AUTHORIZATION="Bearer %s" % self.sender_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

