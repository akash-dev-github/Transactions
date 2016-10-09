from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from proj_utils import ModelTemplate, CURRENCY_CHOICES


class Account(ModelTemplate):
    owner = models.ForeignKey(User, db_index=True)  # indexed as user might have multiple accounts
    balance = models.DecimalField(max_digits=32, decimal_places=8)
    currency = models.CharField(choices=CURRENCY_CHOICES, max_length=8)

    class Meta(ModelTemplate.Meta):
        db_table = "account"

    def __unicode__(self):
        return "%s's account with balance %s %s" % (self.owner.username, self.balance, self.currency)

