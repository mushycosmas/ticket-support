from django.db import models


class KPIReport(models.Model):
    # Ticket counts
    total_tickets = models.PositiveIntegerField(default=0)
    resolved_tickets = models.PositiveIntegerField(default=0)
    open_tickets = models.PositiveIntegerField(default=0)

    # SLA / performance metric
    avg_resolution_time = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # Optional useful KPI fields (recommended for your BPM system)
    escalated_tickets = models.PositiveIntegerField(default=0)
    reopened_tickets = models.PositiveIntegerField(default=0)
    csat_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0
    )

    sla_compliance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "KPI Report"
        verbose_name_plural = "KPI Reports"

    def __str__(self):
        return f"KPI Report - {self.created_at.date()}"