import stripe
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view, inline_serializer

from .models import Payment
from .serializers import (
    PaymentSerializer,
    CheckoutSessionSerializer,
    PaymentConfirmationSerializer,
)

def get_stripe():
    """
    Safely initialize Stripe with secret key.
    Prevents crash at Django import time.
    """
    stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")
    return stripe

checkout_session_response_serializer = inline_serializer(
    name='CheckoutSessionResponse',
    fields={
        'session_id': serializers.CharField(),
        'checkout_url': serializers.URLField(),
        'payment_id': serializers.IntegerField(),
    },
)

stripe_webhook_response_serializer = inline_serializer(
    name='StripeWebhookResponse',
    fields={
        'status': serializers.CharField(),
    },
)

payment_confirmation_response_serializer = inline_serializer(
    name='PaymentConfirmationResponse',
    fields={
        'payment': PaymentSerializer(),
        'stripe_status': serializers.CharField(),
        'payment_status': serializers.CharField(),
        'fulfilled': serializers.BooleanField(),
    },
)


def sync_payment_from_checkout_session(payment, session):
    from apps.notifications.models import Notification
    from apps.notifications.tasks import create_notification, send_order_confirmation_email
    from apps.tickets.models import TicketType, Ticket

    stripe_status = session.get('status')
    stripe_payment_status = session.get('payment_status')

    if stripe_payment_status != 'paid':
        if stripe_status == 'expired':
            payment.status = Payment.Status.FAILED
        payment.metadata = {
            **payment.metadata,
            'stripe_status': stripe_status,
            'stripe_payment_status': stripe_payment_status,
        }
        payment.save(update_fields=['status', 'metadata', 'updated_at'])
        return False

    with transaction.atomic():
        payment = Payment.objects.select_for_update().get(pk=payment.pk)

        if payment.status == Payment.Status.COMPLETED:
            return True

        metadata = session.get("metadata", {}) or payment.metadata
        ticket_type = TicketType.objects.select_for_update().get(
            id=metadata["ticket_type_id"]
        )
        quantity = int(metadata.get("quantity", 1))

        payment.status = Payment.Status.COMPLETED
        payment.provider_payment_id = session.get("payment_intent", "") or session.get("id", "")
        payment.metadata = {
            **payment.metadata,
            'stripe_status': stripe_status,
            'stripe_payment_status': stripe_payment_status,
            'fulfilled_quantity': quantity,
        }
        payment.save(update_fields=['status', 'provider_payment_id', 'metadata', 'updated_at'])

        created_tickets = []
        for _ in range(quantity):
            ticket = Ticket.objects.create(
                ticket_type=ticket_type,
                event=ticket_type.event,
                attendee=payment.user,
                status=Ticket.Status.CONFIRMED,
                price_paid=ticket_type.price,
            )
            ticket.attach_qr_code()
            created_tickets.append(ticket)

        ticket_type.quantity_sold += quantity
        ticket_type.save(update_fields=['quantity_sold'])

    create_notification(
        recipient=payment.user,
        notification_type=Notification.Type.PAYMENT_CONFIRMED,
        title='Payment confirmed',
        message=f'Your payment for "{payment.event.title}" was confirmed and {quantity} ticket(s) were issued.',
        data={
            'payment_id': payment.id,
            'session_id': payment.provider_session_id,
            'tickets': [str(ticket.ticket_number) for ticket in created_tickets],
        },
    )

    send_order_confirmation_email.delay(payment.id)

    return True

@extend_schema_view(
    list=extend_schema(tags=['Payments'], summary='List payments'),
    retrieve=extend_schema(
        tags=['Payments'],
        summary='Retrieve a payment',
        parameters=[OpenApiParameter('id', int, OpenApiParameter.PATH)],
    ),
)
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

    @extend_schema(
        tags=['Payments'],
        summary='Create a Stripe checkout session',
        description='Validates ticket availability, creates a Stripe Checkout session, and stores a pending payment record.',
        request=CheckoutSessionSerializer,
        responses={
            200: checkout_session_response_serializer,
            400: OpenApiResponse(description='Stripe error or invalid quantity'),
            404: OpenApiResponse(description='Ticket type not found'),
        },
    )
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
            metadata = {
                "user_id": str(request.user.id),
                "ticket_type_id": str(ticket_type.id),
                "quantity": str(quantity),
            }
            session = stripe_client.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": getattr(settings, "STRIPE_CURRENCY", "usd"),
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
                client_reference_id=str(request.user.id),
                customer_email=request.user.email,
                metadata=metadata,
            )

            payment = Payment.objects.create(
                user=request.user,
                event=ticket_type.event,
                amount=ticket_type.price * quantity,
                currency=getattr(settings, "STRIPE_CURRENCY", "usd").upper(),
                provider=Payment.Provider.STRIPE,
                provider_session_id=session.id,
                status=Payment.Status.PENDING,
                metadata=metadata,
            )

            return Response({
                "session_id": session.id,
                "checkout_url": session.url,
                "payment_id": payment.id,
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaymentConfirmationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Payments'],
        summary='Confirm a Stripe payment',
        description='Retrieves the Stripe Checkout session, synchronizes the local payment record, and confirms whether ticket fulfillment has completed.',
        request=PaymentConfirmationSerializer,
        responses={
            200: payment_confirmation_response_serializer,
            400: OpenApiResponse(description='Missing or invalid confirmation payload'),
            404: OpenApiResponse(description='Payment or Stripe session not found'),
        },
    )
    def post(self, request):
        serializer = PaymentConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = self._get_payment(request, serializer.validated_data)
        stripe_client = get_stripe()

        try:
            session = stripe_client.checkout.Session.retrieve(payment.provider_session_id)
        except stripe.error.StripeError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        fulfilled = sync_payment_from_checkout_session(payment, session)

        payment.refresh_from_db()
        return Response({
            'payment': PaymentSerializer(payment).data,
            'stripe_status': session.get('status', ''),
            'payment_status': session.get('payment_status', ''),
            'fulfilled': fulfilled,
        })

    def _get_payment(self, request, data):
        queryset = Payment.objects.all() if getattr(request.user, 'role', None) == 'admin' else Payment.objects.filter(user=request.user)

        if data.get('payment_id'):
            return get_object_or_404(queryset, pk=data['payment_id'])

        return get_object_or_404(queryset, provider_session_id=data['session_id'])

class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Payments'],
        summary='Stripe webhook',
        description='Receives Stripe webhook events and completes ticket fulfillment for successful checkout sessions.',
        request=None,
        responses={
            200: stripe_webhook_response_serializer,
            400: OpenApiResponse(description='Invalid webhook payload or signature'),
        },
    )
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

        event_type = event["type"]
        event_object = event["data"]["object"]

        if event_type in {
            "checkout.session.completed",
            "checkout.session.async_payment_succeeded",
        }:
            self._handle_checkout_complete(event_object)
        elif event_type in {
            "checkout.session.async_payment_failed",
            "checkout.session.expired",
        }:
            self._handle_checkout_failure(event_object, event_type)

        return Response({"status": "ok"})

    def _handle_checkout_complete(self, session):
        try:
            payment = Payment.objects.get(provider_session_id=session["id"])
        except Payment.DoesNotExist:
            return

        sync_payment_from_checkout_session(payment, session)

    def _handle_checkout_failure(self, session, event_type):
        try:
            payment = Payment.objects.get(provider_session_id=session["id"])
        except Payment.DoesNotExist:
            return

        metadata = payment.metadata.copy()
        metadata['failure_event'] = event_type
        metadata['stripe_status'] = session.get('status')
        metadata['stripe_payment_status'] = session.get('payment_status')

        payment.status = Payment.Status.FAILED
        payment.metadata = metadata
        payment.save(update_fields=['status', 'metadata', 'updated_at'])
