from django.urls import path
from .views import CreatePaymentIntentView, VerifyPaymentView, PaymentConfigView
from .webhooks import stripe_webhook


urlpatterns = [
    path('create-intent/', CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('verify/', VerifyPaymentView.as_view(), name='verify_payment'),
    path('config/', PaymentConfigView.as_view(), name='payment_config'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
]
