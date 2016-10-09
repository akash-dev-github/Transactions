from __future__ import unicode_literals

from django.db import models

from accounts.models import ModelTemplate, Account, CURRENCY_CHOICES


class Transaction(ModelTemplate):
    from_account = models.ForeignKey(Account)
    to_account = models.ForeignKey(Account)
    amount = models.DecimalField(max_digits=32, decimal_places=8)
    status = models.CharField(max_length=64)

    # not be same accounts