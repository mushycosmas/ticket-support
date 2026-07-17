# apps/users/views/team_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from ..models import Team, User
from ..serializers import (
    TeamSerializer,
    UserSerializer,
    UserTicketSerializer
)

from .mixins import TeamViewSetPermissions, TicketStatsMixin
from .base import BaseViewSetMixin

from apps.tickets.models import Ticket


class TeamViewSet(
    TeamViewSetPermissions,
    TicketStatsMixin,
    BaseViewSetMixin,
    viewsets.ModelViewSet
):

    queryset = Team.objects.all()
    serializer_class = TeamSerializer


    # ======================================================
    # QUERYSET
    # ======================================================

    def get_queryset(self):

        user = self.request.user

        if user.role and user.role.name == "ADMIN":
            return Team.objects.all()

        elif user.role and user.role.name in [
            "TEAM_LEAD",
            "AGENT"
        ]:
            return Team.objects.filter(
                members=user
            )

        return Team.objects.none()



    # ======================================================
    # LIST TEAMS
    # ======================================================

    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()

        search = request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                name__icontains=search
            )


        serializer = TeamSerializer(
            queryset,
            many=True
        )

        return Response({
            "count": queryset.count(),
            "results": serializer.data
        })



    # ======================================================
    # RETRIEVE TEAM
    # ======================================================

    def retrieve(self, request, *args, **kwargs):

        team = self.get_object()

        serializer = self.get_serializer(team)

        data = serializer.data

        data["member_count"] = team.members.count()

        return Response(data)



    # ======================================================
    # CREATE TEAM
    # ======================================================

    def create(self, request, *args, **kwargs):

        error = self.check_admin_permission(
            request.user
        )

        if error:
            return error


        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        team = serializer.save()


        return Response(
            TeamSerializer(team).data,
            status=status.HTTP_201_CREATED
        )



    # ======================================================
    # UPDATE TEAM
    # ======================================================

    def update(self, request, *args, **kwargs):

        error = self.check_admin_permission(
            request.user
        )

        if error:
            return error


        team = self.get_object()


        serializer = self.get_serializer(
            team,
            data=request.data,
            partial=kwargs.pop(
                "partial",
                False
            )
        )


        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()


        return Response(
            serializer.data
        )



    # ======================================================
    # DELETE TEAM
    # ======================================================

    def destroy(self, request, *args, **kwargs):

        error = self.check_admin_permission(
            request.user
        )

        if error:
            return error


        team = self.get_object()

        team.delete()


        return Response({
            "message":
            "Team deleted successfully"
        })



    # ======================================================
    # TEAM MEMBERS
    # ======================================================

    @action(
        detail=True,
        methods=["get"]
    )
    def members(self, request, pk=None):

        team = self.get_object()

        members = team.members.all()


        serializer = UserSerializer(
            members,
            many=True
        )


        return Response(serializer.data)



    # ======================================================
    # ADD MEMBER
    # ======================================================

    @action(
        detail=True,
        methods=["post"]
    )
    def add_member(self, request, pk=None):

        team = self.get_object()

        user_id = request.data.get(
            "user_id"
        )

        current_user = request.user


        is_admin = (
            current_user.role
            and current_user.role.name == "ADMIN"
        )


        is_team_lead = (
            current_user.role
            and current_user.role.name == "TEAM_LEAD"
            and team.members.filter(
                id=current_user.id
            ).exists()
        )


        if not (
            is_admin
            or is_team_lead
        ):
            return Response(
                {
                    "error":
                    "You don't have permission"
                },
                status=403
            )



        if not user_id:

            return Response(
                {
                    "error":
                    "user_id is required"
                },
                status=400
            )



        try:

            user = User.objects.get(
                id=user_id
            )


            # Add user to many-to-many
            team.members.add(user)



            return Response({

                "message":
                f"{user.get_full_name() or user.username} added to {team.name}",

                "member_count":
                team.members.count()

            })


        except User.DoesNotExist:

            return Response(
                {
                    "error":
                    "User not found"
                },
                status=404
            )



    # ======================================================
    # REMOVE MEMBER
    # ======================================================

    @action(
        detail=True,
        methods=["delete"]
    )
    def remove_member(self, request, pk=None):

        team = self.get_object()

        user_id = request.data.get(
            "user_id"
        )


        if not user_id:

            return Response(
                {
                    "error":
                    "user_id required"
                },
                status=400
            )



        try:

            user = User.objects.get(
                id=user_id
            )


            team.members.remove(user)



            return Response({

                "message":
                "Member removed successfully",

                "member_count":
                team.members.count()

            })


        except User.DoesNotExist:

            return Response(
                {
                    "error":
                    "User not found"
                },
                status=404
            )



    # ======================================================
    # TEAM TICKETS
    # ======================================================

    @action(
        detail=True,
        methods=["get"]
    )
    def tickets(self, request, pk=None):

        team = self.get_object()


        tickets = Ticket.objects.filter(
            team=team
        ).order_by(
            "-created_at"
        )


        serializer = UserTicketSerializer(
            tickets,
            many=True
        )


        return Response({

            "count":
            tickets.count(),

            "results":
            serializer.data

        })



    # ======================================================
    # TEAM STATISTICS
    # ======================================================

    @action(
        detail=True,
        methods=["get"]
    )
    def stats(self, request, pk=None):

        team = self.get_object()


        tickets = Ticket.objects.filter(
            team=team
        )


        return Response({

            "total_tickets":
            tickets.count(),

            "open":
            tickets.filter(
                status="OPEN"
            ).count(),

            "in_progress":
            tickets.filter(
                status="IN_PROGRESS"
            ).count(),

            "resolved":
            tickets.filter(
                status="RESOLVED"
            ).count(),

            "closed":
            tickets.filter(
                status="CLOSED"
            ).count()

        })



    # ======================================================
    # MY TEAM
    # ======================================================

    @action(
        detail=False,
        methods=["get"]
    )
    def my_team(self, request):

        user = request.user


        team = Team.objects.filter(
            members=user
        ).first()


        if not team:

            return Response(
                {
                    "error":
                    "You are not assigned to any team"
                },
                status=404
            )


        serializer = TeamSerializer(team)


        return Response(serializer.data)



    # ======================================================
    # AVAILABLE MEMBERS
    # ======================================================

    @action(
        detail=False,
        methods=["get"]
    )
    def available_members(self, request):

        users = User.objects.exclude(
            teams__isnull=False
        )


        search = request.query_params.get(
            "search"
        )


        if search:

            users = users.filter(

                Q(username__icontains=search)
                |
                Q(email__icontains=search)
                |
                Q(first_name__icontains=search)
                |
                Q(last_name__icontains=search)

            )


        serializer = UserSerializer(
            users,
            many=True
        )


        return Response(
            serializer.data
        )



    # ======================================================
    # ALL TEAMS
    # ======================================================

    @action(
        detail=False,
        methods=["get"]
    )
    def all_teams(self, request):

        teams = Team.objects.all().order_by(
            "name"
        )


        serializer = TeamSerializer(
            teams,
            many=True
        )


        return Response({

            "count":
            teams.count(),

            "results":
            serializer.data

        })