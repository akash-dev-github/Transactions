from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account


class SnippetDetail(APIView):
    """
    GET a list of accounts.
    """
    def get(self, request, format=None):
        accounts = Account.active_objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data)
