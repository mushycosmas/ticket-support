from django.db import models
from apps.tickets.models import Ticket


class SLA(models.Model):

    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)

    response_time_limit = models.IntegerField(default=60)  # minutes
    resolution_time_limit = models.IntegerField(default=240)  # minutes

    is_breached = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)