from rest_framework import serializers
from .models import FAQ, FAQFeedback


class FAQSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    channel_name = serializers.CharField(source="channel.name", read_only=True)

    class Meta:
        model = FAQ
        fields = [
            "id",
            "category",
            "category_name",
            "channel",
            "channel_name",
            "question",
            "answer",
            "slug",
            "is_active",
            "is_featured",
            "views",
            "sort_order",
            "created_at",
        ]


class FAQFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQFeedback
        fields = [
            "id",
            "faq",
            "helpful",
            "comment",
            "created_at",
        ]