from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account
from accounts.serializers import AccountSerializer


class AccountAPIs(APIView):
    """
        GET: To list accounts related to a user | POST: add an account(SuperUser only)
    """
    serializer_class = AccountSerializer

    def get(self, request):
        accounts = Account.active_objects.all()
        serializer = self.serializer_class(accounts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
