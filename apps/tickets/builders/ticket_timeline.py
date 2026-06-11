class TicketTimelineBuilder:

    @staticmethod
    def build(ticket):
        timeline = []

        for h in ticket.histories.all().order_by("-created_at"):

            user = "System"
            if h.created_by:
                user = h.created_by.get_full_name() or h.created_by.username

            timeline.append({
                "id": h.id,
                "date": h.created_at.isoformat(),
                "action": h.action,
                "message": TicketTimelineBuilder.message(h),
                "user": user,
                "comment": h.comment,
            })

        return timeline

    @staticmethod
    def message(history):
        if history.action == "CREATED":
            return "Ticket created"
        if history.action == "ASSIGNED":
            return "Ticket assigned"
        if history.action == "COMMENTED":
            return history.comment or "Comment added"
        if history.action == "STATUS_CHANGED":
            return f"{history.old_status} → {history.new_status}"

        return "Update"