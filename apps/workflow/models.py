from django.db import models


class AssignmentRule(models.Model):

    name = models.CharField(max_length=255)

    priority = models.CharField(max_length=20, default='medium')
    auto_assign = models.BooleanField(default=True)

    max_load_per_agent = models.IntegerField(default=10)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name