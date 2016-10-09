# #### Any project wide helper stuff sits here

import datetime
from django.db import models


CURRENCY_CHOICES = (
    ('BTC', 'bitcoin'),
    ('ETH', 'etherium'),
    ('PHP', 'pesos'),
)
# #### In case senders account currency is diff, debit_number != credit_number, conversion will be required
# Following mapping holds conversion of 1 bitcoin to currency in key
# ideally these should come from a third party service API but due to the scope of project
# conversion rate is hardcoded with current market values (9th October, 2016)
CURRENCY_CONVERSION = {
    "BTC": 1,
    "ETH": 50.4429,
    "PHP": 29848.13,
}


# #### custom Manager to return only active objects
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(is_active=True)


# #### all Models extend this class and thus have all its fields
class ModelTemplate(models.Model):
    is_active = models.BooleanField(default=True)
    added_dttm = models.DateTimeField(default=datetime.datetime.now, editable=False)
    last_modified_dttm = models.DateTimeField(default=datetime.datetime.now)

    objects = models.Manager()  # The default manager.
    active_objects = ActiveManager()  # active objects only in queryset

    class Meta:
        abstract = True  # making it usable only when extended
