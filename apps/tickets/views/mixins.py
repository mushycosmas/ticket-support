from rest_framework.decorators import action
from rest_framework.response import Response
import logging

from ..services.ticket_service import TicketService
from apps.notifications.services.ticket_sms_service import TicketSMSService

# Create loggers
logger = logging.getLogger(__name__)
sms_logger = logging.getLogger('sms')


class TicketResolveMixin:
    """
    Mixin for resolving tickets with SMS notification.
    """
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Resolve a ticket and send SMS notification to the customer.
        """
        ticket = self.get_object()
        comment = request.data.get('comment', '')
        
        # Log resolve attempt
        sms_logger.info("=" * 70)
        sms_logger.info(f"📌 RESOLVING TICKET: {ticket.ticket_number}")
        sms_logger.info(f"   Customer: {ticket.customer.full_name if ticket.customer else 'N/A'}")
        sms_logger.info(f"   Phone: {ticket.customer.phone if ticket.customer else 'N/A'}")
        sms_logger.info(f"   Comment: {comment[:50] if comment else 'None'}")
        sms_logger.info("=" * 70)
        
        try:
            # Resolve the ticket
            ticket = TicketService.resolve(ticket, request, comment=comment)
            sms_logger.info(f"✅ Ticket {ticket.ticket_number} resolved successfully")
            
            # ============================================================
            # 📱 SEND SMS WHEN TICKET IS RESOLVED
            # ============================================================
            sms_sent = False
            if ticket.customer and ticket.customer.phone:
                try:
                    sms_logger.info("📱 Sending SMS notification...")
                    sms_sent = TicketSMSService.send_ticket_resolved_sms(ticket, comment)
                    
                    if sms_sent:
                        sms_logger.info(f"✅ SMS sent successfully to {ticket.customer.phone}")
                    else:
                        sms_logger.warning(f"⚠️ SMS failed for {ticket.customer.phone}")
                except Exception as e:
                    sms_logger.error(f"❌ Error sending SMS: {str(e)}")
            else:
                sms_logger.info("ℹ️ No customer phone number - SMS not sent")
            
            sms_logger.info("=" * 70)
            
            # Return response with SMS status
            serializer = self.get_serializer(ticket)
            response_data = serializer.data
            response_data['sms_sent'] = sms_sent if ticket.customer and ticket.customer.phone else None
            
            return Response({
                'success': True,
                'message': 'Ticket resolved successfully',
                'data': response_data,
                'sms_sent': sms_sent if ticket.customer and ticket.customer.phone else None
            })
            
        except ValueError as e:
            sms_logger.error(f"❌ Error resolving ticket: {str(e)}")
            sms_logger.info("=" * 70)
            return Response({
                "success": False,
                "error": str(e)
            }, status=400)
        except Exception as e:
            sms_logger.error(f"❌ Unexpected error: {str(e)}")
            sms_logger.info("=" * 70)
            return Response({
                "success": False,
                "error": "An unexpected error occurred while resolving the ticket"
            }, status=500)


class TicketCloseMixin:
    """
    Mixin for closing tickets with SMS notification.
    """
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        Close a ticket and send SMS notification to the customer.
        """
        ticket = self.get_object()
        comment = request.data.get('comment', '')
        
        # Log close attempt
        sms_logger.info("=" * 70)
        sms_logger.info(f"📌 CLOSING TICKET: {ticket.ticket_number}")
        sms_logger.info(f"   Customer: {ticket.customer.full_name if ticket.customer else 'N/A'}")
        sms_logger.info(f"   Phone: {ticket.customer.phone if ticket.customer else 'N/A'}")
        sms_logger.info(f"   Comment: {comment[:50] if comment else 'None'}")
        sms_logger.info("=" * 70)
        
        try:
            # Close the ticket
            ticket = TicketService.close(ticket, request, comment=comment)
            sms_logger.info(f"✅ Ticket {ticket.ticket_number} closed successfully")
            
            # ============================================================
            # 📱 SEND SMS WHEN TICKET IS CLOSED
            # ============================================================
            sms_sent = False
            if ticket.customer and ticket.customer.phone:
                try:
                    sms_logger.info("📱 Sending SMS notification...")
                    sms_sent = TicketSMSService.send_ticket_closed_sms(ticket)
                    
                    if sms_sent:
                        sms_logger.info(f"✅ SMS sent successfully to {ticket.customer.phone}")
                    else:
                        sms_logger.warning(f"⚠️ SMS failed for {ticket.customer.phone}")
                except Exception as e:
                    sms_logger.error(f"❌ Error sending SMS: {str(e)}")
            else:
                sms_logger.info("ℹ️ No customer phone number - SMS not sent")
            
            sms_logger.info("=" * 70)
            
            # Return response with SMS status
            serializer = self.get_serializer(ticket)
            response_data = serializer.data
            response_data['sms_sent'] = sms_sent if ticket.customer and ticket.customer.phone else None
            
            return Response({
                'success': True,
                'message': 'Ticket closed successfully',
                'data': response_data,
                'sms_sent': sms_sent if ticket.customer and ticket.customer.phone else None
            })
            
        except ValueError as e:
            sms_logger.error(f"❌ Error closing ticket: {str(e)}")
            sms_logger.info("=" * 70)
            return Response({
                "success": False,
                "error": str(e)
            }, status=400)
        except Exception as e:
            sms_logger.error(f"❌ Unexpected error: {str(e)}")
            sms_logger.info("=" * 70)
            return Response({
                "success": False,
                "error": "An unexpected error occurred while closing the ticket"
            }, status=500)


class TicketReopenMixin:
    """
    Mixin for reopening tickets with SMS notification.
    """
    
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """
        Reopen a ticket and send SMS notification to the customer.
        """
        ticket = self.get_object()
        comment = request.data.get('comment', '')
        
        # Log reopen attempt
        sms_logger.info("=" * 70)
        sms_logger.info(f"📌 REOPENING TICKET: {ticket.ticket_number}")
        sms_logger.info(f"   Customer: {ticket.customer.full_name if ticket.customer else 'N/A'}")
        sms_logger.info(f"   Phone: {ticket.customer.phone if ticket.customer else 'N/A'}")
        sms_logger.info(f"   Comment: {comment[:50] if comment else 'None'}")
        sms_logger.info("=" * 70)
        
        try:
            ticket = TicketService.reopen(ticket, request, comment=comment)
            sms_logger.info(f"✅ Ticket {ticket.ticket_number} reopened successfully")
            
            # ============================================================
            # 📱 SEND SMS WHEN TICKET IS REOPENED
            # ============================================================
            sms_sent = False
            if ticket.customer and ticket.customer.phone:
                try:
                    sms_logger.info("📱 Sending SMS notification...")
                    sms_sent = TicketSMSService.send_ticket_reopened_sms(ticket)
                    
                    if sms_sent:
                        sms_logger.info(f"✅ SMS sent successfully to {ticket.customer.phone}")
                    else:
                        sms_logger.warning(f"⚠️ SMS failed for {ticket.customer.phone}")
                except Exception as e:
                    sms_logger.error(f"❌ Error sending SMS: {str(e)}")
            else:
                sms_logger.info("ℹ️ No customer phone number - SMS not sent")
            
            sms_logger.info("=" * 70)
            
            # Return response with SMS status
            serializer = self.get_serializer(ticket)
            response_data = serializer.data
            response_data['sms_sent'] = sms_sent if ticket.customer and ticket.customer.phone else None
            
            return Response({
                'success': True,
                'message': 'Ticket reopened successfully',
                'data': response_data,
                'sms_sent': sms_sent if ticket.customer and ticket.customer.phone else None
            })
            
        except ValueError as e:
            sms_logger.error(f"❌ Error reopening ticket: {str(e)}")
            sms_logger.info("=" * 70)
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            sms_logger.error(f"❌ Unexpected error: {str(e)}")
            sms_logger.info("=" * 70)
            return Response({
                "success": False,
                "error": "An unexpected error occurred while reopening the ticket"
            }, status=500)


class TicketAssignMixin:
    """
    Mixin for assigning tickets with optional SMS notification.
    """
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign a ticket to an agent.
        """
        ticket = self.get_object()
        
        # Log assign attempt
        sms_logger.info("=" * 70)
        sms_logger.info(f"📌 ASSIGNING TICKET: {ticket.ticket_number}")
        sms_logger.info(f"   Customer: {ticket.customer.full_name if ticket.customer else 'N/A'}")
        sms_logger.info(f"   Phone: {ticket.customer.phone if ticket.customer else 'N/A'}")
        sms_logger.info("=" * 70)
        
        try:
            ticket = TicketService.assign(ticket, request)
            sms_logger.info(f"✅ Ticket {ticket.ticket_number} assigned to {ticket.assigned_to.get_full_name() if ticket.assigned_to else 'N/A'}")
            
            # ============================================================
            # 📱 SEND SMS WHEN TICKET IS ASSIGNED (Optional)
            # ============================================================
            sms_sent = False
            if ticket.customer and ticket.customer.phone and ticket.assigned_to:
                try:
                    sms_logger.info("📱 Sending SMS notification...")
                    sms_sent = TicketSMSService.send_ticket_assigned_sms(ticket)
                    
                    if sms_sent:
                        sms_logger.info(f"✅ SMS sent successfully to {ticket.customer.phone}")
                    else:
                        sms_logger.warning(f"⚠️ SMS failed for {ticket.customer.phone}")
                except Exception as e:
                    sms_logger.error(f"❌ Error sending SMS: {str(e)}")
            else:
                sms_logger.info("ℹ️ No customer phone or assigned agent - SMS not sent")
            
            sms_logger.info("=" * 70)
            
            # Return response with SMS status
            serializer = self.get_serializer(ticket)
            response_data = serializer.data
            response_data['sms_sent'] = sms_sent if ticket.customer and ticket.customer.phone and ticket.assigned_to else None
            
            return Response({
                'success': True,
                'message': 'Ticket assigned successfully',
                'data': response_data,
                'sms_sent': sms_sent if ticket.customer and ticket.customer.phone and ticket.assigned_to else None
            })
            
        except ValueError as e:
            sms_logger.error(f"❌ Error assigning ticket: {str(e)}")
            sms_logger.info("=" * 70)
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            sms_logger.error(f"❌ Unexpected error: {str(e)}")
            sms_logger.info("=" * 70)
            return Response({
                "success": False,
                "error": "An unexpected error occurred while assigning the ticket"
            }, status=500)


class TicketCommentMixin:
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        ticket = self.get_object()
        try:
            history = TicketService.add_comment(ticket, request)
            return Response({
                'status': 'Comment added',
                'history_id': history.id,
                'comment': history.comment,
                'created_at': history.created_at.isoformat()
            })
        except ValueError as e:
            return Response({"error": str(e)}, status=400)


class TicketOverdueMixin:
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        from django.utils import timezone
        from datetime import timedelta
        threshold = timezone.now() - timedelta(days=2)
        tickets = self.get_queryset().filter(
            created_at__lt=threshold
        ).exclude(status__in=['RESOLVED', 'CLOSED'])
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)


class TicketAgingMixin:
    @action(detail=False, methods=['get'])
    def aging(self, request):
        from django.utils import timezone
        tickets = self.get_queryset().exclude(status__in=['RESOLVED', 'CLOSED'])
        result = []
        for ticket in tickets:
            days_old = (timezone.now() - ticket.created_at).days
            result.append({
                'id': ticket.id,
                'ticket_number': ticket.ticket_number,
                'title': ticket.title,
                'status': ticket.status,
                'priority': ticket.priority,
                'created_at': ticket.created_at.isoformat(),
                'days_old': days_old,
                'assigned_to_name': ticket.assigned_to.get_full_name() or ticket.assigned_to.username if ticket.assigned_to else None,
                'customer_name': ticket.customer.full_name if ticket.customer else None,
            })
        result.sort(key=lambda x: x['days_old'], reverse=True)
        return Response(result)