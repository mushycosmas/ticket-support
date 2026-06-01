from django.db import models
from apps.tickets.models import Ticket
from apps.users.models import User


class QAReview(models.Model):

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)

    score = models.FloatField(default=0)

    comment = models.TextField(null=True, blank=True)

    passed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)