from .sms_service import SMSService


class TicketSMSService:

    # ============================================================
    # CUSTOMER NOTIFICATIONS
    # ============================================================

    @staticmethod
    def send_ticket_created_sms(ticket):
        """
        Send SMS when ticket is created (to customer).
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
        Send SMS when ticket is resolved (to customer).
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
        Send SMS when ticket is closed (to customer).
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
        Send SMS when ticket is reopened (to customer).
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
        Send SMS when ticket is assigned to an agent (to customer).
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
        Send SMS when ticket is escalated (to customer).
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

    # ============================================================
    # STAFF NOTIFICATIONS (Assigned Agent, Team Lead, Admin)
    # ============================================================

    @staticmethod
    def _get_staff_recipients(ticket):
        """
        Get staff recipients for SMS notifications.
        Includes: assigned agent, their team lead, and admins.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        recipients = []

        # 1. Get assigned_to (the agent)
        if ticket.assigned_to and ticket.assigned_to.phone:
            recipients.append({
                'phone': ticket.assigned_to.phone,
                'name': ticket.assigned_to.get_full_name() or ticket.assigned_to.username,
                'role': 'Assigned Agent'
            })

        # 2. Get Team Lead of the agent's team
        if ticket.assigned_to:
            # Get the team(s) the agent belongs to
            agent_teams = ticket.assigned_to.teams.all()
            for team in agent_teams:
                # Find team leads in this team
                team_leads = team.members.filter(role__name='TEAM_LEAD')
                for lead in team_leads:
                    if lead.phone and lead.id != ticket.assigned_to.id:  # Don't duplicate if agent is also team lead
                        recipients.append({
                            'phone': lead.phone,
                            'name': lead.get_full_name() or lead.username,
                            'role': f'Team Lead ({team.name})'
                        })
        
        # If no agent team found, try using ticket's team
        if not recipients and ticket.team:
            team_leads = ticket.team.members.filter(role__name='TEAM_LEAD')
            for lead in team_leads:
                if lead.phone:
                    recipients.append({
                        'phone': lead.phone,
                        'name': lead.get_full_name() or lead.username,
                        'role': f'Team Lead ({ticket.team.name})'
                    })

        # 3. Get all Admins
        admins = User.objects.filter(role__name='ADMIN')
        for admin in admins:
            if admin.phone:
                recipients.append({
                    'phone': admin.phone,
                    'name': admin.get_full_name() or admin.username,
                    'role': 'Admin'
                })

        # Remove duplicates
        seen_phones = set()
        unique_recipients = []
        for r in recipients:
            if r['phone'] not in seen_phones:
                seen_phones.add(r['phone'])
                unique_recipients.append(r)

        return unique_recipients

    @staticmethod
    def send_ticket_created_to_staff(ticket):
        """
        Send SMS to assigned agent, team lead, and admin when ticket is created.
        """
        recipients = TicketSMSService._get_staff_recipients(ticket)

        if not recipients:
            print(
                f"[SMS] No staff recipients found for ticket {ticket.ticket_number}"
            )
            return False

        # Prepare message
        customer_name = ticket.customer.full_name if ticket.customer else "Unknown"
        message = (
            f"📋 New Ticket Created\n"
            f"Ticket: {ticket.ticket_number}\n"
            f"Customer: {customer_name}\n"
            f"Priority: {ticket.priority}\n"
            f"Status: {ticket.status}\n"
            f"Please check and take action."
        )

        print(
            f"[SMS] Sending ticket-created to staff | "
            f"Ticket: {ticket.ticket_number} | "
            f"Recipients: {len(recipients)}"
        )

        # Send to all recipients
        results = []
        for recipient in recipients:
            print(
                f"[SMS] Sending to {recipient['role']}: {recipient['name']} | "
                f"Phone: {recipient['phone']}"
            )
            result = SMSService.send_sms(
                recipient=recipient['phone'],
                message=message,
            )
            results.append({
                'phone': recipient['phone'],
                'role': recipient['role'],
                'success': result
            })

        print(
            f"[SMS] Staff notifications sent: {sum(1 for r in results if r['success'])}/{len(results)} successful"
        )

        return results

    @staticmethod
    def send_ticket_assigned_to_staff(ticket):
        """
        Send SMS to assigned agent, team lead, and admin when ticket is assigned.
        """
        recipients = TicketSMSService._get_staff_recipients(ticket)

        if not recipients:
            print(
                f"[SMS] No staff recipients found for ticket {ticket.ticket_number}"
            )
            return False

        # Prepare message
        customer_name = ticket.customer.full_name if ticket.customer else "Unknown"
        assigned_to_name = ticket.assigned_to.get_full_name() or ticket.assigned_to.username if ticket.assigned_to else "Unassigned"
        message = (
            f"📌 Ticket Assigned\n"
            f"Ticket: {ticket.ticket_number}\n"
            f"Customer: {customer_name}\n"
            f"Assigned To: {assigned_to_name}\n"
            f"Priority: {ticket.priority}\n"
            f"Please check and take action."
        )

        print(
            f"[SMS] Sending ticket-assigned to staff | "
            f"Ticket: {ticket.ticket_number} | "
            f"Recipients: {len(recipients)}"
        )

        # Send to all recipients
        results = []
        for recipient in recipients:
            print(
                f"[SMS] Sending to {recipient['role']}: {recipient['name']} | "
                f"Phone: {recipient['phone']}"
            )
            result = SMSService.send_sms(
                recipient=recipient['phone'],
                message=message,
            )
            results.append({
                'phone': recipient['phone'],
                'role': recipient['role'],
                'success': result
            })

        print(
            f"[SMS] Staff notifications sent: {sum(1 for r in results if r['success'])}/{len(results)} successful"
        )

        return results

    @staticmethod
    def send_ticket_resolved_to_staff(ticket, resolution_notes=''):
        """
        Send SMS to assigned agent, team lead, and admin when ticket is resolved.
        """
        recipients = TicketSMSService._get_staff_recipients(ticket)

        if not recipients:
            print(
                f"[SMS] No staff recipients found for ticket {ticket.ticket_number}"
            )
            return False

        # Prepare message
        customer_name = ticket.customer.full_name if ticket.customer else "Unknown"
        resolved_by = ticket.resolved_by.get_full_name() if hasattr(ticket, 'resolved_by') and ticket.resolved_by else "Staff"
        message = (
            f"✅ Ticket Resolved\n"
            f"Ticket: {ticket.ticket_number}\n"
            f"Customer: {customer_name}\n"
            f"Resolved By: {resolved_by}\n"
            f"{f'Notes: {resolution_notes[:50]}' if resolution_notes else ''}\n"
            f"Please verify and close if needed."
        )

        print(
            f"[SMS] Sending ticket-resolved to staff | "
            f"Ticket: {ticket.ticket_number} | "
            f"Recipients: {len(recipients)}"
        )

        # Send to all recipients
        results = []
        for recipient in recipients:
            print(
                f"[SMS] Sending to {recipient['role']}: {recipient['name']} | "
                f"Phone: {recipient['phone']}"
            )
            result = SMSService.send_sms(
                recipient=recipient['phone'],
                message=message,
            )
            results.append({
                'phone': recipient['phone'],
                'role': recipient['role'],
                'success': result
            })

        print(
            f"[SMS] Staff notifications sent: {sum(1 for r in results if r['success'])}/{len(results)} successful"
        )

        return results

    @staticmethod
    def send_ticket_closed_to_staff(ticket):
        """
        Send SMS to assigned agent, team lead, and admin when ticket is closed.
        """
        recipients = TicketSMSService._get_staff_recipients(ticket)

        if not recipients:
            print(
                f"[SMS] No staff recipients found for ticket {ticket.ticket_number}"
            )
            return False

        # Prepare message
        customer_name = ticket.customer.full_name if ticket.customer else "Unknown"
        message = (
            f"✅ Ticket Closed\n"
            f"Ticket: {ticket.ticket_number}\n"
            f"Customer: {customer_name}\n"
            f"Status: {ticket.status}\n"
            f"Ticket has been closed."
        )

        print(
            f"[SMS] Sending ticket-closed to staff | "
            f"Ticket: {ticket.ticket_number} | "
            f"Recipients: {len(recipients)}"
        )

        # Send to all recipients
        results = []
        for recipient in recipients:
            print(
                f"[SMS] Sending to {recipient['role']}: {recipient['name']} | "
                f"Phone: {recipient['phone']}"
            )
            result = SMSService.send_sms(
                recipient=recipient['phone'],
                message=message,
            )
            results.append({
                'phone': recipient['phone'],
                'role': recipient['role'],
                'success': result
            })

        print(
            f"[SMS] Staff notifications sent: {sum(1 for r in results if r['success'])}/{len(results)} successful"
        )

        return results

    # ============================================================
    # COMBINED NOTIFICATIONS (Customer + Staff)
    # ============================================================

    @staticmethod
    def send_all_ticket_created_notifications(ticket):
        """
        Send all notifications when ticket is created (customer + staff).
        """
        results = {
            'customer': TicketSMSService.send_ticket_created_sms(ticket),
            'staff': TicketSMSService.send_ticket_created_to_staff(ticket),
        }
        return results

    @staticmethod
    def send_all_ticket_assigned_notifications(ticket):
        """
        Send all notifications when ticket is assigned (customer + staff).
        """
        results = {
            'customer': TicketSMSService.send_ticket_assigned_sms(ticket),
            'staff': TicketSMSService.send_ticket_assigned_to_staff(ticket),
        }
        return results

    @staticmethod
    def send_all_ticket_resolved_notifications(ticket, resolution_notes=''):
        """
        Send all notifications when ticket is resolved (customer + staff).
        """
        results = {
            'customer': TicketSMSService.send_ticket_resolved_sms(ticket, resolution_notes),
            'staff': TicketSMSService.send_ticket_resolved_to_staff(ticket, resolution_notes),
        }
        return results

    @staticmethod
    def send_all_ticket_closed_notifications(ticket):
        """
        Send all notifications when ticket is closed (customer + staff).
        """
        results = {
            'customer': TicketSMSService.send_ticket_closed_sms(ticket),
            'staff': TicketSMSService.send_ticket_closed_to_staff(ticket),
        }
        return results

    @staticmethod
    def send_all_ticket_reopened_notifications(ticket):
        """
        Send all notifications when ticket is reopened (customer + staff).
        """
        results = {
            'customer': TicketSMSService.send_ticket_reopened_sms(ticket),
            'staff': TicketSMSService.send_ticket_created_to_staff(ticket),
        }
        return results