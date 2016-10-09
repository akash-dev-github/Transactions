from rest_framework import serializers

from payments.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['from_account', 'to_account', 'amount']
