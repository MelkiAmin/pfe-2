import stripe
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .serializers import PaymentSerializer, CheckoutSessionSerializer


def get_stripe():
    """
    Safely initialize Stripe with secret key.
    Prevents crash at Django import time.
    """
    stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")
    return stripe


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == "admin":
            return Payment.objects.all()
        return Payment.objects.filter(user=user)


class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        stripe_client = get_stripe()

        serializer = CheckoutSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.tickets.models import TicketType

        try:
            ticket_type = TicketType.objects.get(
                id=serializer.validated_data["ticket_type_id"]
            )
        except TicketType.DoesNotExist:
            return Response(
                {"detail": "Ticket type not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        quantity = serializer.validated_data["quantity"]

        if ticket_type.available_quantity < quantity:
            return Response(
                {"detail": "Not enough tickets available."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = stripe_client.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"{ticket_type.event.title} - {ticket_type.name}"
                        },
                        "unit_amount": int(ticket_type.price * 100),
                    },
                    "quantity": quantity,
                }],
                mode="payment",
                success_url=serializer.validated_data["success_url"],
                cancel_url=serializer.validated_data["cancel_url"],
                metadata={
                    "user_id": request.user.id,
                    "ticket_type_id": ticket_type.id,
                    "quantity": quantity,
                },
            )

            payment = Payment.objects.create(
                user=request.user,
                event=ticket_type.event,
                amount=ticket_type.price * quantity,
                provider=Payment.Provider.STRIPE,
                provider_session_id=session.id,
                status=Payment.Status.PENDING,
            )

            return Response({
                "session_id": session.id,
                "checkout_url": session.url,
                "payment_id": payment.id,
            })

        except stripe.error.StripeError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        stripe_client = get_stripe()

        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe_client.Webhook.construct_event(
                payload,
                sig_header,
                getattr(settings, "STRIPE_WEBHOOK_SECRET", ""),
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event["type"] == "checkout.session.completed":
            self._handle_checkout_complete(event["data"]["object"])

        return Response({"status": "ok"})

    def _handle_checkout_complete(self, session):
        from apps.tickets.models import TicketType, Ticket

        try:
            payment = Payment.objects.get(
                provider_session_id=session["id"]
            )

            payment.status = Payment.Status.COMPLETED
            payment.provider_payment_id = session.get("payment_intent", "")
            payment.save()

            metadata = session.get("metadata", {})
            ticket_type = TicketType.objects.get(
                id=metadata["ticket_type_id"]
            )
            quantity = int(metadata.get("quantity", 1))

            for _ in range(quantity):
                Ticket.objects.create(
                    ticket_type=ticket_type,
                    event=ticket_type.event,
                    attendee=payment.user,
                    status=Ticket.Status.CONFIRMED,
                    price_paid=ticket_type.price,
                )

            ticket_type.quantity_sold += quantity
            ticket_type.save()

        except Payment.DoesNotExist:
            pass