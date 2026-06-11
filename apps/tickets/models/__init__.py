"""
DO NOT force-import all models here.
Django automatically discovers models via INSTALLED_APPS.
Keeping this file minimal avoids circular imports and startup errors.
"""

from .ticket import Ticket
from .customer import Customer
from .attachment import TicketAttachment
from .history import TicketHistory
from .issue_template import IssueTemplate

__all__ = [
    "Ticket",
    "Customer",
    "TicketAttachment",
    "TicketHistory",
    "IssueTemplate",
]