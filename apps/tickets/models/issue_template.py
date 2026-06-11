from django.db import models

from apps.categories.models import Category
from apps.priorities.models import Priority
from apps.channels.models import Channel


class IssueTemplate(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True
    )

    description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issue_templates"
    )

    suggested_priority = models.ForeignKey(
        Priority,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issue_templates"
    )

    # Allowed channels for this template
    channels = models.ManyToManyField(
        Channel,
        blank=True,
        related_name="issue_templates"
    )

    steps_to_reproduce = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "issue_templates"
        ordering = ["name"]
        verbose_name = "Issue Template"
        verbose_name_plural = "Issue Templates"

    def __str__(self):
        return self.name

    @property
    def category_name(self):
        return self.category.name if self.category else None

    @property
    def priority_name(self):
        return self.suggested_priority.name if self.suggested_priority else None

    @property
    def channel_names(self):
        return list(
            self.channels.values_list("name", flat=True)
        )