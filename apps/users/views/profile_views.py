# apps/users/views/profile_views.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..serializers import ChangePasswordSerializer


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        # 1. Check old password
        if not user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Set new password
        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": "Password changed successfully"},
            status=status.HTTP_200_OK
        )