from django.db import models

# Base abstract models for common fields
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class AuditableModel(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        abstract = True