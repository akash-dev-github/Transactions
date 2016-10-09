from __future__ import unicode_literals

from django.db import models

from accounts.models import ModelTemplate, Account


class Transaction(ModelTemplate):
    from_account = models.ForeignKey(Account, related_name="transaction_from_acc")
    to_account = models.ForeignKey(Account, related_name="transaction_to_acc")
    amount = models.DecimalField(max_digits=32, decimal_places=8)

    class Meta(ModelTemplate.Meta):
        db_table = "transaction"

    def __unicode__(self):
        return "%s to %s an amount %s" % (self.from_account, self.to_account, self.amount)
