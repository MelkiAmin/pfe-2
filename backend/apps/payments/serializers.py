from rest_framework import serializers
from .models import Payment, Refund

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'event',
            'amount',
            'currency',
            'status',
            'provider',
            'provider_payment_id',
            'provider_session_id',
            'metadata',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'status',
            'provider_payment_id',
            'provider_session_id',
            'metadata',
            'created_at',
            'updated_at',
        ]

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


class PaymentConfirmationSerializer(serializers.Serializer):
    session_id = serializers.CharField(required=False)
    payment_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        if not attrs.get('session_id') and not attrs.get('payment_id'):
            raise serializers.ValidationError(
                'Either session_id or payment_id is required.'
            )
        return attrs
