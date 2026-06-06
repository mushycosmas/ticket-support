# Import all models so Django can find them
from .ticket import Ticket
from .attachment import TicketAttachment
from .history import TicketHistory
from .customer import Customer

__all__ = ['Ticket', 'TicketAttachment', 'TicketHistory', 'Customer']