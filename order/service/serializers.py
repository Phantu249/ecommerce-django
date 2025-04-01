from rest_framework import serializers
from .models import Order, OrderState, OrderItem

class OrderStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderState
        fields = "__all__"

class PaymentMethodSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=50, required=True)

class PaymentStateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=50, required=True)

class NameSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)

class RoleSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=50, required=True)

class ProductImageSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    path = serializers.CharField(max_length=255, required=True)

class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=50, required=True)
    description = serializers.CharField(max_length=255, required=True)

class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=50, required=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    product_image = ProductImageSerializer(many=True, required=True)
    description = serializers.CharField(max_length=255, required=True)
    stock = serializers.IntegerField(required=True, min_value=0)
    category = CategorySerializer(required=True)

class OrderItemRequestSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

class OrderItemResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['quantity', 'price']
    product = ProductSerializer()

class CitySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=50, required=True)

class DistrictSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=50, required=True)
    city = CitySerializer()

class WardSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=50, required=True)
    district = DistrictSerializer()

class AddressUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    detail = serializers.CharField(max_length=255, required=True)
    ward = WardSerializer()

class AddressSerializer(serializers.Serializer):
    ward = WardSerializer(required=True)
    detail = serializers.CharField(max_length=255, required=True)

class AddressRequestOrderSerializer(serializers.Serializer):
    ward_id = serializers.IntegerField(required=True)
    detail = serializers.CharField(max_length=255, required=True)

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=50, required=True)
    email = serializers.EmailField(required=True)
    address = AddressUserSerializer()
    phone_number = serializers.CharField(max_length=10, required=True)
    name = NameSerializer()
    role = RoleSerializer()

class OrderRequestSerializer(serializers.Serializer):
    address = AddressRequestOrderSerializer(required=True)
    phone_number = serializers.CharField(max_length=10, required=True)
    payment_method_id = serializers.IntegerField(required=True)
    items = OrderItemRequestSerializer(many=True, required=True)

class OrderResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['phone_number', 'created_at', 'id']

    address = AddressSerializer()
    order_state = OrderStateSerializer()
    user = UserSerializer()
    payment_method = PaymentMethodSerializer()
    payment_state = PaymentStateSerializer()
    items = OrderItemRequestSerializer(many=True, required=True)
    order_state = OrderStateSerializer()

class PageSerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=1, required=True)  # Current page number
    per_page = serializers.IntegerField(min_value=1, required=True)  # Number of items per page
    total_pages = serializers.IntegerField(min_value=0, required=True)  # Total number of pages
    content = serializers.ListField(
        child=serializers.DictField(),  # Each item in the list is a dictionary
        required=True
    )