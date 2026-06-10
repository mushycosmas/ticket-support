# models.py
from django.db import models

class Channel(models.Model):
    STATUS_PRIVATE = "private"
    STATUS_PUBLIC = "public"

    STATUS_CHOICES = [
        (STATUS_PRIVATE, "Private"),
        (STATUS_PUBLIC, "Public"),
    ]

    name = models.CharField(max_length=50)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PRIVATE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name