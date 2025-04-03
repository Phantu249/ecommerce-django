import os
from http.client import responses

from django.core.paginator import Paginator
from django.db.transaction import atomic
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from .permissions import IsAuth


class CartView(APIView):
    permission_classes = [IsAuth]

    def get(self, request):
        page = request.query_params.get('page', 1)
        per_page = request.query_params.get('per_page', 10)
        user_id = request.user['id']
        cart, created = Cart.objects.get_or_create(id=user_id)
        paginator = Paginator(cart.items.all(), per_page)
        try:
            cart_items = paginator.page(page)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CartItemSerializer(cart_items, many=True)

        response = {
            'items': serializer.data,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,

        }
        return Response(response, status=status.HTTP_200_OK)

    @atomic
    def post(self, request):
        user_id = request.user['id']
        product_id = request.data.get('id')
        quantity = request.data.get('quantity')

        if not product_id or not quantity:
            return Response({'error': 'Thiếu id hoặc quantity'}, status=status.HTTP_400_BAD_REQUEST)

        cart, created = Cart.objects.get_or_create(id=user_id)

        # Kiểm tra product có tồn tại trong Product Service
        try:
            response = requests.get(f"{settings.PRODUCT_SERVICE_URL}/{product_id}")
            if response.status_code != 200:
                return Response({'error': 'Product không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        except requests.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        product_data = response.json()
        # Kiểm tra product có bị ẩn k
        try:
            if not product_data.get('is_active', True):
                return Response({'error': 'Product đã bị ẩn'}, status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, ValueError):
            return Response({'error': 'Dữ liệu sản phẩm không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra stock
        try:
            if product_data['stock'] < quantity:
                return Response({'error': 'Không đủ hàng trong kho'}, status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, ValueError):
            return Response({'error': 'Dữ liệu sản phẩm không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart, product_id=product_id, defaults={'quantity': quantity}
        )
        if not item_created:
            # Nếu sản phẩm đã có trong giỏ hàng, cập nhật số lượng
            cart_item.quantity += quantity
            # Kiểm tra stock trước khi cập nhật
            if product_data['stock'] < cart_item.quantity:
                return Response({'error': 'Không đủ hàng trong kho'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.save()
        return Response(status=status.HTTP_200_OK)


class CartItemDeleteView(APIView):
    permission_classes = [IsAuth]

    @atomic
    def delete(self, request, product_id):
        user_id = request.user['id']
        try:
            cart = Cart.objects.get(id=user_id)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            return Response(status=status.HTTP_200_OK)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)


class CartToOrderView(APIView):
    permission_classes = [IsAuth]

    @atomic
    def post(self, request):
        user_id = request.user['id']
        data = request.data

        # Kiểm tra các trường bắt buộc
        required_fields = ['address', 'payment_method_id', 'phone_number', 'items']
        if not all(field in data for field in required_fields):
            return Response({'error': 'Thiếu các trường bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)

        # Chuẩn bị dữ liệu gửi tới Order Service
        order_data = {
            'address': data['address'],
            'payment_method_id': data['payment_method_id'],
            'phone_number': data['phone_number'],
            'items': [
                {
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'price': item['price']
                } for item in data['items']
            ]
        }

        # Gọi API Order Service
        try:
            response = requests.post(
                os.getenv('ORDER_SERVICE_URL') + '/create',
                json=order_data,
                headers={'Authorization': request.headers.get('Authorization'), 'Cross-Service': 'Cart Service'}
            )
            response.raise_for_status()  # Ném lỗi nếu không phải 200
        except requests.RequestException as e:
            return Response({'error': f"Lỗi khi tạo order: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Nếu tạo order thành công, xóa giỏ hàng
        try:
            cart = Cart.objects.get(id=user_id)
            CartItem.objects.filter(cart=cart, product_id__in=[i['product_id'] for i in data['items']]).delete()
            return Response(status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart không tồn tại'}, status=status.HTTP_404_NOT_FOUND)