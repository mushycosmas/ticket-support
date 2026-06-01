from django.db import models
from apps.users.models import User


class AuditLog(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    action = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)

    object_id = models.IntegerField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)