import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Payment


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    """
    POST: Create a Stripe PaymentIntent for $1 resume download.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Create PaymentIntent with Stripe
            intent = stripe.PaymentIntent.create(
                amount=100,  # $1.00 in cents
                currency='usd',
                automatic_payment_methods={
                    'enabled': True,
                },
                metadata={
                    'user_id': str(request.user.id),
                    'username': request.user.username,
                }
            )

            # Create payment record in database
            payment = Payment.objects.create(
                user=request.user,
                stripe_payment_intent_id=intent.id,
                amount=100,
                status='pending'
            )

            return Response({
                'client_secret': intent.client_secret,
                'payment_id': payment.id,
            })

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class VerifyPaymentView(APIView):
    """
    POST: Verify payment before allowing PDF download.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_id = request.data.get('payment_id')

        if not payment_id:
            return Response({'error': 'Missing payment_id'}, status=400)

        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=404)

        # Check if payment already used
        if payment.resume_downloaded:
            return Response({'error': 'Payment already used for download'}, status=400)

        # Verify payment status with Stripe
        try:
            intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)

            if intent.status == 'succeeded':
                payment.status = 'succeeded'
                payment.save()
                return Response({
                    'verified': True,
                    'payment_id': payment.id,
                })
            else:
                return Response({
                    'verified': False,
                    'error': f'Payment status: {intent.status}'
                }, status=400)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=400)


class PaymentConfigView(APIView):
    """
    GET: Return Stripe publishable key for frontend.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        })
