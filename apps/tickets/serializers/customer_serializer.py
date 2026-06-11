from rest_framework import serializers
from apps.tickets.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="full_name", read_only=True)
    customer_email = serializers.EmailField(source="email", read_only=True)
    customer_phone = serializers.CharField(source="phone", read_only=True)

    # 👇 ADD HUMAN READABLE GENDER
    gender_display = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "id",
            "customer_name",
            "customer_email",
            "customer_phone",

            "nida_number",
            "gender",
            "gender_display",   # ✅ important fix

            "company_name",
            "address",
            "city",
            "country",

            "total_tickets",
            "total_resolved",
            "total_open",
            "created_at",
        ]

        read_only_fields = [
            "total_tickets",
            "total_resolved",
            "total_open",
        ]

    # ======================
    # GENDER DISPLAY FIX
    # ======================
    def get_gender_display(self, obj):
        if not obj.gender:
            return None
        return obj.get_gender_display()