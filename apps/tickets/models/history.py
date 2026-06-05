from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth import get_user_model
from .base import AuditableModel

User = get_user_model()

class TicketHistory(AuditableModel):
    class ActionType(models.TextChoices):
        CREATED = 'CREATED', 'Ticket Created'
        UPDATED = 'UPDATED', 'Ticket Updated'
        COMMENTED = 'COMMENTED', 'Comment Added'
        STATUS_CHANGED = 'STATUS_CHANGED', 'Status Changed'
        PRIORITY_CHANGED = 'PRIORITY_CHANGED', 'Priority Changed'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        UNASSIGNED = 'UNASSIGNED', 'Unassigned'
        ATTACHMENT = 'ATTACHMENT', 'Attachment Added'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'
        REOPENED = 'REOPENED', 'Reopened'
    
    ticket = models.ForeignKey("Ticket", on_delete=models.CASCADE, related_name="histories")
    action = models.CharField(max_length=50, choices=ActionType.choices, db_index=True)
    
    # Change tracking
    old_status = models.CharField(max_length=50, null=True, blank=True)
    new_status = models.CharField(max_length=50, null=True, blank=True)
    old_priority = models.CharField(max_length=20, null=True, blank=True)
    new_priority = models.CharField(max_length=20, null=True, blank=True)
    old_assignee = models.CharField(max_length=255, null=True, blank=True)
    new_assignee = models.CharField(max_length=255, null=True, blank=True)
    
    # Content
    comment = models.TextField(null=True, blank=True, validators=[MinLengthValidator(1)])
    metadata = models.JSONField(default=dict, blank=True)
    
    # User who performed action
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="ticket_histories")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['ticket', '-created_at']),
            models.Index(fields=['action', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.ticket.ticket_number} - {self.get_action_display()} by {self.created_by or 'System'}"
    
    @property
    def display_message(self):
        messages = {
            self.ActionType.CREATED: "Ticket created",
            self.ActionType.COMMENTED: self.comment,
            self.ActionType.STATUS_CHANGED: f"Status changed from {self.old_status} to {self.new_status}",
            self.ActionType.PRIORITY_CHANGED: f"Priority changed from {self.old_priority} to {self.new_priority}",
            self.ActionType.ASSIGNED: f"Assigned to {self.new_assignee}",
            self.ActionType.UNASSIGNED: f"Unassigned from {self.old_assignee}",
            self.ActionType.RESOLVED: "Ticket resolved",
            self.ActionType.CLOSED: "Ticket closed",
            self.ActionType.ATTACHMENT: self._get_attachment_message(),
        }
        return messages.get(self.action, self.metadata.get('message', 'Ticket updated'))
    
    def _get_attachment_message(self):
        attachments = self.metadata.get('attachments', [])
        if attachments:
            return f"Added {len(attachments)} attachment(s): {', '.join(attachments)}"
        return "Attachment(s) added"
    
    @property
    def display_type(self):
        type_map = {
            self.ActionType.CREATED: 'info',
            self.ActionType.COMMENTED: 'comment',
            self.ActionType.STATUS_CHANGED: 'update',
            self.ActionType.PRIORITY_CHANGED: 'update',
            self.ActionType.ASSIGNED: 'update',
            self.ActionType.UNASSIGNED: 'update',
            self.ActionType.RESOLVED: 'resolution',
            self.ActionType.CLOSED: 'resolution',
            self.ActionType.ATTACHMENT: 'update',
        }
        return type_map.get(self.action, 'info')
    
    # Helper methods for logging
    @classmethod
    def log_creation(cls, ticket, user=None, ip_address=None):
        return cls.objects.create(
            ticket=ticket, action=cls.ActionType.CREATED,
            created_by=user, ip_address=ip_address,
            metadata={'message': f'Ticket "{ticket.title}" was created'}
        )
    
    @classmethod
    def log_comment(cls, ticket, comment, user=None, ip_address=None):
        return cls.objects.create(
            ticket=ticket, action=cls.ActionType.COMMENTED,
            comment=comment, created_by=user, ip_address=ip_address
        )
    
    @classmethod
    def log_status_change(cls, ticket, old_status, new_status, user=None, ip_address=None):
        return cls.objects.create(
            ticket=ticket, action=cls.ActionType.STATUS_CHANGED,
            old_status=old_status, new_status=new_status,
            created_by=user, ip_address=ip_address
        )