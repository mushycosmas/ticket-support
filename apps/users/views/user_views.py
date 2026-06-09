from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import User
from ..serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserTicketSerializer
)

from .mixins import UserViewSetPermissions, UserQuerySetMixin, TicketStatsMixin
from .base import BaseViewSetMixin


class UserViewSet(
    UserViewSetPermissions,
    UserQuerySetMixin,
    TicketStatsMixin,
    BaseViewSetMixin,
    viewsets.ModelViewSet
):
    """
    USER MANAGEMENT VIEWSET (FIXED VERSION)
    """

    permission_classes = [IsAuthenticated]  # ✅ SAFETY FALLBACK

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        elif self.action == "tickets":
            return UserTicketSerializer
        return UserSerializer

    # ======================
    # LIST (FIXED DRF STYLE)
    # ======================
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    # ======================
    # CREATE
    # ======================
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    # ======================
    # UPDATE
    # ======================
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        error = self.check_self_or_admin(request.user, instance)
        if error:
            return error

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(UserSerializer(user).data)

    # ======================
    # DELETE
    # ======================
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        error = self.check_admin_permission(request.user)
        if error:
            return error

        if user.id == request.user.id:
            return Response(
                {"error": "You cannot delete your own account"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.delete()
        return Response(
            {"message": "User deleted successfully"},
            status=status.HTTP_200_OK
        )

    # ======================
    # TICKETS
    # ======================
    @action(detail=True, methods=["get"])
    def tickets(self, request, pk=None):
        user = self.get_object()

        error = self.check_self_or_admin(request.user, user)
        if error:
            return error

        status_filter = request.query_params.get("status")
        priority_filter = request.query_params.get("priority")

        tickets, total = self.get_user_tickets(
            user,
            status_filter,
            priority_filter
        )

        serializer = UserTicketSerializer(tickets, many=True)

        return Response({
            "count": total,
            "results": serializer.data
        })

    # ======================
    # STATS
    # ======================
    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        user = self.get_object()

        error = self.check_self_or_admin(request.user, user)
        if error:
            return error

        stats = self.get_user_ticket_stats(user)
        return Response(stats)

    # ======================
    # RESET PASSWORD
    # ======================
    @action(detail=True, methods=["post"])
    def reset_password(self, request, pk=None):
        user = self.get_object()

        error = self.check_admin_permission(request.user)
        if error:
            return error

        default_password = "support123"
        user.set_password(default_password)
        user.save()

        return Response(
            {"message": "Password reset successfully"},
            status=status.HTTP_200_OK
        )