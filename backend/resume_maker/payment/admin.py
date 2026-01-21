from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'status', 'resume_downloaded', 'created_at']
    list_filter = ['status', 'resume_downloaded', 'created_at']
    search_fields = ['user__username', 'stripe_payment_intent_id']
    readonly_fields = ['stripe_payment_intent_id', 'created_at', 'updated_at']
