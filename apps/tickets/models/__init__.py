# Import all models so Django can find them
from .ticket import Ticket
from .attachment import TicketAttachment
from .history import TicketHistory
from .customer import Customer  # Add this line

__all__ = ['Ticket', 'TicketAttachment', 'TicketHistory', 'Customer']