from django.db import models

class Priority(models.Model):
    name = models.CharField(max_length=50)
    level = models.IntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=20, default="secondary")

    def __str__(self):
        return self.name