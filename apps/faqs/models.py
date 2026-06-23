from django.db import models
from django.utils.text import slugify

from apps.categories.models import Category
from apps.channels.models import Channel


class FAQ(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="faqs"
    )

    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="faqs"
    )

    question = models.CharField(max_length=255)
    answer = models.TextField()

    slug = models.SlugField(unique=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    views = models.PositiveIntegerField(default=0)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "faqs"
        ordering = ["sort_order", "question"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.question)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.question


class FAQFeedback(models.Model):
    faq = models.ForeignKey(
        FAQ,
        on_delete=models.CASCADE,
        related_name="feedbacks"
    )

    helpful = models.BooleanField()
    comment = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.faq.question}"