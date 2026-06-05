# All choices in one place
class TicketChannel:
    CHOICES = [
        ('PHONE', 'Phone'),
        ('WALKIN', 'Walk-in'),
        ('EMAIL', 'Email'),
        ('CHAT', 'Chat'),
        ('WEB', 'Web Form'),
    ]

class TicketStatus:
    CHOICES = [
        ('OPEN', 'Open'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

class TicketPriority:
    CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]