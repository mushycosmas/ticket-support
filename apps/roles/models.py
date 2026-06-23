from django.db import models
from django.contrib.auth.models import Permission


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    permissions = models.ManyToManyField(Permission, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    # =========================
    # FIX: FORCE UPPERCASE ROLE
    # =========================
    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
class SystemPermissionGroup(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name