class TicketWorkflow:

    @staticmethod
    def can_assign(ticket):
        return ticket.status == "OPEN"

    @staticmethod
    def assign(ticket, agent_name):
        ticket.status = "ASSIGNED"
        ticket.assigned_to = agent_name
        ticket.save()
        return ticket

    @staticmethod
    def start_progress(ticket):
        if ticket.status in ["ASSIGNED"]:
            ticket.status = "IN_PROGRESS"
            ticket.save()
        return ticket

    @staticmethod
    def resolve(ticket):
        ticket.status = "RESOLVED"
        ticket.save()
        return ticket

    @staticmethod
    def close(ticket):
        ticket.status = "CLOSED"
        ticket.save()
        return ticket