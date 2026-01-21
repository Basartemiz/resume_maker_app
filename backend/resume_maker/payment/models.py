from django.db import models
from django.contrib.auth.models import User


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    amount = models.IntegerField(default=100)  # Amount in cents ($1 = 100 cents)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    resume_downloaded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.status}"
