from django.db import transaction
import httpx
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem, OrderState, OrderStateHistory
from .serializers import *
from .clients import (
    get_user_info, get_orders_by_user, get_order_items_by_order,
    get_address_by_ward_id, get_user_by_id, get_payment_state,
    get_payment_method, get_payment_state_by_name, get_address_by_ward
)
import os
import logging

# Lấy URL của product-service từ biến môi trường
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://product-service:8001/api/product')

class OrderView(APIView):
    """
    API View to list all orders or create a new order.
    """
    def get(self, request, *args, **kwargs):
        auth_token = request.headers.get('Authorization')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        total_pages = 0
        content = []

        user = get_user_info(auth_token)
        logging.info(f"User info: {user}")
        if not user:
            return Response({"detail": "Invalid user data"}, status=status.HTTP_400_BAD_REQUEST)

        role = user.get('role')
        if not role:
            return Response({"detail": "Role not found"}, status=status.HTTP_400_BAD_REQUEST)

        if role.get('name') != 'admin':
            data = get_orders_by_user(user.get('id'), page, per_page)
            if data.get('total_pages') == 0:
                return Response({"page": page, "per_page": per_page, "total_pages": 0, "content": []}, status=status.HTTP_200_OK)
            total_pages = data.get('total_pages')
            user_serializer = UserSerializer(data=user)
            for order in data.get('content'):
                order_items = get_order_items_by_order(order.get('id'))
                address = get_address_by_ward_id(auth_token, order.get('ward_id'), order.get('address'))
                payment_state = PaymentStateSerializer(data=get_payment_state(auth_token, order.get('payment_state_id')))
                payment_method = PaymentMethodSerializer(data=get_payment_method(auth_token, order.get('payment_method_id')))
                order_state = OrderStateSerializer(OrderState.objects.filter(id=order.get('order_state_id')).first())

                order_data = {
                    "id": order.get('id'),
                    "phone_number": order.get('phone_number'),
                    "created_at": order.get('created_at'),
                    "address": address.data if address.is_valid() else None,
                    "order_state": order_state.data if order_state.is_valid() else None,
                    "user": user_serializer.data if user_serializer.is_valid() else None,
                    "payment_method": payment_method.data if payment_method.is_valid() else None,
                    "payment_state": payment_state.data if payment_state.is_valid() else None,
                    "items": order_items,
                }
                content.append(OrderResponseSerializer(data=order_data).data if OrderResponseSerializer(data=order_data).is_valid() else {})

        else:
            orders = Order.objects.all()
            total_pages = (orders.count() + per_page - 1) // per_page
            start = (page - 1) * per_page
            end = start + per_page
            for order in orders[start:end]:
                order_items = get_order_items_by_order(order.id)
                address = get_address_by_ward_id(auth_token, order.ward_id, order.address)
                payment_state = PaymentStateSerializer(data=get_payment_state(auth_token, order.payment_state_id))
                payment_method = PaymentMethodSerializer(data=get_payment_method(auth_token, order.payment_method_id))
                order_state = OrderStateSerializer(order.order_state)
                customer = get_user_by_id(auth_token, order.user_id)

                order_data = {
                    "id": order.id,
                    "phone_number": order.phone_number,
                    "created_at": order.created_at,
                    "address": address.data if address.is_valid() else None,
                    "order_state": order_state.data if order_state.is_valid() else None,
                    "user": customer.data if customer.is_valid() else None,
                    "payment_method": payment_method.data if payment_method.is_valid() else None,
                    "payment_state": payment_state.data if payment_state.is_valid() else None,
                    "items": order_items,
                }
                content.append(OrderResponseSerializer(data=order_data).data if OrderResponseSerializer(data=order_data).is_valid() else {})

        response_data = {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "content": content,
        }
        return Response(response_data, status=status.HTTP_200_OK)

class OrderCreateAPIView(APIView):
    """
    API View to create a new order.
    """
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = OrderRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        auth_token = request.headers.get('AUTHORIZATION')
        user = get_user_info(auth_token)
        if not user or not user.get('id'):
            return Response({"detail": "Invalid user data"}, status=status.HTTP_400_BAD_REQUEST)

        payment_state_data = get_payment_state_by_name(auth_token, "Pending")
        if not payment_state_data:
            return Response({"detail": "Payment state not found"}, status=status.HTTP_400_BAD_REQUEST)

        items = serializer.validated_data['items']
        stock_check_payload = [{"product_id": item['product_id'], "quantity": item['quantity']} for item in items]

        product_service_url = f"{PRODUCT_SERVICE_URL}/stock"
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        try:
            response = httpx.post(product_service_url, json=stock_check_payload, headers=headers)
            if response.status_code != 200:
                return Response({"detail": f"Failed to check stock: {response.text}"}, status=status.HTTP_400_BAD_REQUEST)

            stock_data = response.json()
            for stock_item in stock_data:
                product_id = stock_item.get('product_id')
                available_stock = stock_item.get('available_stock', 0)
                requested_quantity = next(item['quantity'] for item in items if item['product_id'] == product_id)
                if available_stock < requested_quantity:
                    return Response(
                        {"detail": f"Insufficient stock for product {product_id}. Available: {available_stock}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        except httpx.RequestError as e:
            return Response({"detail": f"Failed to connect to product service: {str(e)}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        order = Order.objects.create(
            user_id=user.get('id'),
            phone_number=serializer.validated_data['phone_number'],
            order_state=OrderState.objects.get(name="Pending"),
            ward_id=serializer.validated_data['address']['ward_id'],
            address=serializer.validated_data['address']['detail'],
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=item['price']
            )

        update_stock_payload = [{"product_id": item['product_id'], "quantity": -item['quantity']} for item in items]
        response = httpx.post(product_service_url, json=update_stock_payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to update stock: {response.text}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderRetrieveDestroyAPIView(APIView):
    """
    API View to retrieve or delete an order.
    """
    def get(self, request, *args, **kwargs):
        auth_token = request.headers.get('AUTHORIZATION')
        user = get_user_info(auth_token)
        if not user:
            return Response({"detail": "Invalid user data"}, status=status.HTTP_400_BAD_REQUEST)

        order_id = self.kwargs.get('pk')  # Sửa thành 'pk'
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.get('id') != order.user_id and user.get('role', {}).get('name') != 'admin':
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        order_items = get_order_items_by_order(order.id)
        address = get_address_by_ward_id(auth_token, order.ward_id, order.address)
        payment_state = PaymentStateSerializer(data=get_payment_state(auth_token, order.payment_state_id))
        payment_method = PaymentMethodSerializer(data=get_payment_method(auth_token, order.payment_method_id))
        order_state = OrderStateSerializer(order.order_state)
        customer = get_user_by_id(auth_token, order.user_id)

        order_data = {
            "id": order.id,
            "phone_number": order.phone_number,
            "created_at": order.created_at,
            "address": address.data if address.is_valid() else None,
            "order_state": order_state.data if order_state.is_valid() else None,
            "user": customer.data if customer.is_valid() else None,
            "payment_method": payment_method.data if payment_method.is_valid() else None,
            "payment_state": payment_state.data if payment_state.is_valid() else None,
            "items": order_items,
        }
        serializer = OrderResponseSerializer(data=order_data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderCancelAPIView(APIView):
    """
    API View to cancel an order and revert stock.
    """
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        auth_token = request.headers.get('AUTHORIZATION')
        user = get_user_info(auth_token)
        if not user:
            return Response({"detail": "Invalid user data"}, status=status.HTTP_400_BAD_REQUEST)

        order_id = self.kwargs.get('pk')
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.get('id') != order.user_id and user.get('role', {}).get('name') != 'admin':
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        order_items = OrderItem.objects.filter(order_id=order_id)
        if not order_items.exists():
            order.order_state = OrderState.objects.get(name="Cancelled")
            order.save()
            return Response({"detail": "Order cancelled successfully."}, status=status.HTTP_200_OK)

        stock_revert_payload = [{"product_id": item.product_id, "quantity": item.quantity} for item in order_items]

        product_service_url = f"{PRODUCT_SERVICE_URL}/stock"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "Cross-Service": "order-service",
        }
        try:
            response = httpx.post(product_service_url, json=stock_revert_payload, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Failed to revert stock: {response.text}")

            order.order_state = OrderState.objects.get(name="Cancelled")
            order.save()
            return Response({"detail": "Order cancelled successfully and stock reverted."}, status=status.HTTP_200_OK)

        except httpx.RequestError as e:
            return Response({"detail": f"Failed to connect to product service: {str(e)}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({"detail": f"Failed to cancel order: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderStateHistoryView(APIView):
    """
    API View to get order state history
    """
    def get(self, request, *args, **kwargs):
        auth_token = request.headers.get('AUTHORIZATION')
        user = get_user_info(auth_token)
        if not user:
            return Response({"detail": "Invalid user data"}, status=status.HTTP_400_BAD_REQUEST)

        order_id = self.kwargs.get('pk')  # Sửa thành 'pk'
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.get('id') != order.user_id and user.get('role', {}).get('name') != 'admin':
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        order_states = OrderStateHistory.objects.filter(order_id=order_id)
        content = [
            {
                "created_at": state.created_at,
                "id": state.id,
                "order_state": OrderStateSerializer(state.order_state).data,
            }
            for state in order_states
        ]
        return Response(content, status=status.HTTP_200_OK)

class ApproveOrderView(APIView):
    def post(self, request, *args, **kwargs):
        auth_token = request.headers.get('AUTHORIZATION')
        state_serializer = StateSerializer(data=request.data)
        if not state_serializer.is_valid():
            return Response(state_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        state = state_serializer.validated_data.get('state')
        user = get_user_info(auth_token)
        if not user:
            return Response({"detail": "Invalid user data"}, status=status.HTTP_400_BAD_REQUEST)

        order_id = self.kwargs.get('pk')  # Sửa thành 'pk'
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.get('role', {}).get('name') != 'admin':
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        order.order_state = OrderState.objects.get(id=state)
        order.save()
        return Response({"detail": "Order approved successfully."}, status=status.HTTP_200_OK)