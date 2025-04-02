from rest_framework import serializers
import requests
from django.conf import settings
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product_id')
    name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.FloatField(source='product.price', read_only=True)
    stock = serializers.IntegerField(source='product.stock', read_only=True)
    img_url = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'name', 'price', 'stock', 'img_url', 'category', 'is_active', 'quantity']

    def get_img_url(self, obj):
        product_data = self._fetch_product(obj.product_id)
        if product_data and 'product_image' in product_data and product_data['product_image']:
            return product_data['product_image'][0]['path']
        return None

    def get_category(self, obj):
        product_data = self._fetch_product(obj.product_id)
        return product_data.get('category') if product_data else None

    def _fetch_product(self, product_id):
        try:
            response = requests.get(f"{settings.PRODUCT_SERVICE_URL}/{product_id}",
                                    headers={'Cross-Service': 'Cart Service'})
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['items']
