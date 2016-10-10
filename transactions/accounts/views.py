from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account
from accounts.serializers import AccountSerializer


class AccountAPIs(APIView):
    """
        GET: To list accounts related to a user | POST: add an account(self account only)
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_acc_objs = Account.active_objects.filter(owner=request.user)  # may have multiple accounts
        serializer = self.serializer_class(user_acc_objs, many=True)
        return Response(
                {
                    "data": serializer.data,
                    "success": True
                },
                status=status.HTTP_200_OK)

    def post(self, request):
        req_data = request.data
        req_data['owner'] = request.user
        if not req_data.get('currency'):
            req_data['currency'] = "PHP"
        req_data["balance"] = 0.0  # during account creation balance should be 0

        serializer = self.serializer_class(data=req_data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "data": serializer.data,
                    "success": True
                },
                status=status.HTTP_201_CREATED)
        return Response(
            {
                "err_msg": serializer.errors,
                "success": False
            },
            status=status.HTTP_400_BAD_REQUEST)
