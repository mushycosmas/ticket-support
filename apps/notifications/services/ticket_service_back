from .sms_service import SMSService


class TicketSMSService:

    @staticmethod
    def send_ticket_created_sms(ticket):
        """
        Send SMS when ticket is created.
        """
        print(
            f"[SMS] Preparing ticket-created SMS | "
            f"Ticket: {ticket.ticket_number} | "
            f"Phone: {ticket.customer_phone}"
        )

        if not ticket.customer_phone:
            print(
                f"[SMS] NOT SENT | "
                f"Ticket: {ticket.ticket_number} | "
                f"Reason: Customer phone is empty"
            )
            return False

        message = (
            f"Your ticket has been created successfully. "
            f"Ticket No: {ticket.ticket_number}. "
            f"Use this number to track your ticket."
        )

        print(
            f"[SMS] Sending ticket-created SMS | "
            f"Recipient: {ticket.customer_phone} | "
            f"Message: {message}"
        )

        result = SMSService.send_sms(
            recipient=ticket.customer_phone,
            message=message,
        )

        print(
            f"[SMS] Ticket-created SMS result: {result}"
        )

        return result

    @staticmethod
    def send_ticket_resolved_sms(ticket, resolution_notes=''):
        """
        Send SMS when ticket is resolved.
        """
        print(
            f"[SMS] Preparing ticket-resolved SMS | "
            f"Ticket: {ticket.ticket_number} | "
            f"Phone: {ticket.customer_phone}"
        )

        if not ticket.customer_phone:
            print(
                f"[SMS] NOT SENT | "
                f"Ticket: {ticket.ticket_number} | "
                f"Reason: Customer phone is empty"
            )
            return False

        message = (
            f"Your ticket {ticket.ticket_number} "
            f"has been resolved successfully. "
            f"{f'Notes: {resolution_notes[:50]}' if resolution_notes else ''}"
            f"Please check your ticket for more details."
        )

        print(
            f"[SMS] Sending ticket-resolved SMS | "
            f"Recipient: {ticket.customer_phone} | "
            f"Message: {message}"
        )

        result = SMSService.send_sms(
            recipient=ticket.customer_phone,
            message=message,
        )

        print(
            f"[SMS] Ticket-resolved SMS result: {result}"
        )

        return result

    @staticmethod
    def send_ticket_closed_sms(ticket):
        """
        Send SMS when ticket is closed.
        """
        print(
            f"[SMS] Preparing ticket-closed SMS | "
            f"Ticket: {ticket.ticket_number} | "
            f"Phone: {ticket.customer_phone}"
        )

        if not ticket.customer_phone:
            print(
                f"[SMS] NOT SENT | "
                f"Ticket: {ticket.ticket_number} | "
                f"Reason: Customer phone is empty"
            )
            return False

        message = (
            f"Your ticket {ticket.ticket_number} "
            f"has been closed successfully. "
            f"Thank you for contacting support."
        )

        print(
            f"[SMS] Sending ticket-closed SMS | "
            f"Recipient: {ticket.customer_phone} | "
            f"Message: {message}"
        )

        result = SMSService.send_sms(
            recipient=ticket.customer_phone,
            message=message,
        )

        print(
            f"[SMS] Ticket-closed SMS result: {result}"
        )

        return result

    @staticmethod
    def send_ticket_reopened_sms(ticket):
        """
        Send SMS when ticket is reopened.
        """
        print(
            f"[SMS] Preparing ticket-reopened SMS | "
            f"Ticket: {ticket.ticket_number} | "
            f"Phone: {ticket.customer_phone}"
        )

        if not ticket.customer_phone:
            print(
                f"[SMS] NOT SENT | "
                f"Ticket: {ticket.ticket_number} | "
                f"Reason: Customer phone is empty"
            )
            return False

        message = (
            f"Your ticket {ticket.ticket_number} "
            f"has been reopened. "
            f"Please check your ticket for updates."
        )

        print(
            f"[SMS] Sending ticket-reopened SMS | "
            f"Recipient: {ticket.customer_phone} | "
            f"Message: {message}"
        )

        result = SMSService.send_sms(
            recipient=ticket.customer_phone,
            message=message,
        )

        print(
            f"[SMS] Ticket-reopened SMS result: {result}"
        )

        return result

    @staticmethod
    def send_ticket_assigned_sms(ticket):
        """
        Send SMS when ticket is assigned to an agent.
        """
        print(
            f"[SMS] Preparing ticket-assigned SMS | "
            f"Ticket: {ticket.ticket_number} | "
            f"Phone: {ticket.customer_phone}"
        )

        if not ticket.customer_phone:
            print(
                f"[SMS] NOT SENT | "
                f"Ticket: {ticket.ticket_number} | "
                f"Reason: Customer phone is empty"
            )
            return False

        assigned_to_name = ticket.assigned_to.get_full_name() or ticket.assigned_to.username if ticket.assigned_to else "Support Agent"

        message = (
            f"Your ticket {ticket.ticket_number} "
            f"has been assigned to {assigned_to_name}. "
            f"They will contact you shortly."
        )

        print(
            f"[SMS] Sending ticket-assigned SMS | "
            f"Recipient: {ticket.customer_phone} | "
            f"Message: {message}"
        )

        result = SMSService.send_sms(
            recipient=ticket.customer_phone,
            message=message,
        )

        print(
            f"[SMS] Ticket-assigned SMS result: {result}"
        )

        return result

    @staticmethod
    def send_ticket_escalated_sms(ticket):
        """
        Send SMS when ticket is escalated.
        """
        print(
            f"[SMS] Preparing ticket-escalated SMS | "
            f"Ticket: {ticket.ticket_number} | "
            f"Phone: {ticket.customer_phone}"
        )

        if not ticket.customer_phone:
            print(
                f"[SMS] NOT SENT | "
                f"Ticket: {ticket.ticket_number} | "
                f"Reason: Customer phone is empty"
            )
            return False

        message = (
            f"Your ticket {ticket.ticket_number} "
            f"has been escalated to priority: {ticket.priority}. "
            f"We are giving it urgent attention."
        )

        print(
            f"[SMS] Sending ticket-escalated SMS | "
            f"Recipient: {ticket.customer_phone} | "
            f"Message: {message}"
        )

        result = SMSService.send_sms(
            recipient=ticket.customer_phone,
            message=message,
        )

        print(
            f"[SMS] Ticket-escalated SMS result: {result}"
        )

        return result