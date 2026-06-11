from ..models import TicketHistory


class TicketTimelineBuilder:
    """Convert ticket history into frontend‑friendly timeline."""

    @staticmethod
    def build(ticket):
        timeline = []
        for history in ticket.histories.all().order_by("-created_at"):
            user_name = "System"
            if history.created_by:
                user_name = history.created_by.get_full_name() or history.created_by.username

            user_role = None
            if history.created_by and hasattr(history.created_by, "role"):
                if history.created_by.role:
                    user_role = history.created_by.role.name if hasattr(history.created_by.role, "name") else str(history.created_by.role)

            message = TicketTimelineBuilder._get_message(history)
            type_map = {
                "CREATED": "info",
                "COMMENTED": "comment",
                "RESOLVED": "resolution",
                "CLOSED": "resolution",
                "REOPENED": "update",
                "ASSIGNED": "update",
                "STATUS_CHANGED": "update",
                "PRIORITY_CHANGED": "update",
            }
            timeline.append({
                "id": history.id,
                "date": history.created_at.isoformat(),
                "action": history.action,
                "message": message,
                "type": type_map.get(history.action, "info"),
                "comment": history.comment,
                "user": user_name,
                "user_role": user_role,
                "is_comment": history.action == "COMMENTED",
                "old_status": history.old_status,
                "new_status": history.new_status,
                "old_priority": history.old_priority,
                "new_priority": history.new_priority,
                "old_assignee": history.old_assignee,
                "new_assignee": history.new_assignee,
            })
        return timeline

    @staticmethod
    def _get_message(history):
        messages = {
            "CREATED": "Ticket created",
            "UPDATED": "Ticket updated",
            "COMMENTED": history.comment or "Comment added",
            "STATUS_CHANGED": f"Status changed from {history.old_status} to {history.new_status}",
            "PRIORITY_CHANGED": f"Priority changed from {history.old_priority} to {history.new_priority}",
            "ASSIGNED": f"Assigned to {history.new_assignee}",
            "UNASSIGNED": f"Unassigned from {history.old_assignee}",
            "RESOLVED": "Ticket resolved",
            "CLOSED": "Ticket closed",
            "REOPENED": "Ticket reopened",
            "ATTACHMENT": "Attachment added",
        }
        return messages.get(history.action, history.metadata.get("message", "Ticket updated"))