from rest_framework import serializers
from .models import Payment, PaymentState, PaymentMethod

class NameAndIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentState  # Dùng chung cho PaymentState và PaymentMethod
        fields = ['id', 'name']

class PaymentSerializer(serializers.ModelSerializer):
    payment_state = NameAndIdSerializer()
    payment_method = NameAndIdSerializer()

    class Meta:
        model = Payment
        fields = ['order_id', 'payment_state', 'payment_method']

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['order_id', 'payment_state', 'payment_method']

class PaymentUpdateSerializer(serializers.Serializer):
    payment_state = serializers.IntegerField(required=False, allow_null=True)
    payment_method = serializers.IntegerField(required=False, allow_null=True)