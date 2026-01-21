import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Payment


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if not sig_header:
        return HttpResponse('Missing signature', status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse('Invalid payload', status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse('Invalid signature', status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_succeeded(payment_intent)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_failed(payment_intent)

    return HttpResponse(status=200)


def handle_payment_succeeded(payment_intent):
    """
    Update payment status when payment succeeds.
    """
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
        payment.status = 'succeeded'
        payment.save()
    except Payment.DoesNotExist:
        pass


def handle_payment_failed(payment_intent):
    """
    Update payment status when payment fails.
    """
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
        payment.status = 'failed'
        payment.save()
    except Payment.DoesNotExist:
        pass
