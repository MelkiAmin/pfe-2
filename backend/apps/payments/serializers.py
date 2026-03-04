from rest_framework import serializers
from .models import Payment, Refund


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'event', 'amount', 'currency', 'status',
                  'provider', 'provider_payment_id', 'created_at']
        read_only_fields = ['status', 'provider_payment_id']


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['id', 'payment', 'amount', 'reason', 'created_at']
        read_only_fields = ['provider_refund_id']


class CheckoutSessionSerializer(serializers.Serializer):
    ticket_type_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=10)
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()