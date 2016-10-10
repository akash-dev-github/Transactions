from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from proj_utils import ModelTemplate


class Account(ModelTemplate):
    BITCOIN = "BTC"
    ETHERIUM = "ETH"
    PESOS = "PHP"
    CURRENCY_CHOICES = (
        (BITCOIN, 'bitcoin'),
        (ETHERIUM, 'etherium'),
        (PESOS, 'pesos'),
    )  # if more added, remember to provide exchange value at proj_utils.CURRENCY_CONVERSION
    owner = models.ForeignKey(User, db_index=True)  # indexed as user might have multiple accounts
    balance = models.DecimalField(max_digits=32, decimal_places=8)
    currency = models.CharField(choices=CURRENCY_CHOICES, max_length=8)

    class Meta(ModelTemplate.Meta):
        db_table = "account"

    @python_2_unicode_compatible
    def __str__(self):
        return "%s's account with balance %s %s" % (self.owner.username, self.balance, self.currency)

