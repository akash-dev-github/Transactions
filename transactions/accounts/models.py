from __future__ import unicode_literals

from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

CURRENCY_CHOICES = (
    ('BT', 'bitcoin'),
    ('ET', 'ether'),
    ('PHP', 'pesos'),
)


# custom Manager to return only active objects
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(is_active=True)


# all Models extend this class and thus have all its fields
class ModelTemplate(models.Model):
    is_active = models.BooleanField(default=True)
    added_dttm = models.DateTimeField(default=datetime.now, editable=False)
    last_modified_dttm = models.DateTimeField(default=datetime.now)

    objects = models.Manager()  # The default manager.
    active_objects = ActiveManager()  # active objects only in queryset

    class Meta:
        abstract = True  # making it usable only when extended


class Account(ModelTemplate):
    owner = models.ForeignKey(User)
    balance = models.DecimalField(max_digits=32, decimal_places=8)
    currency = models.CharField(choices=CURRENCY_CHOICES, max_length=8)

    class Meta(ModelTemplate.Meta):
        db_table = "account"

    def __unicode__(self):
        return "s%'s account with balance %s %s" % (self.owner.username, self.balance, self.currency)

