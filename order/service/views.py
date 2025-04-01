from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem, OrderState, OrderStateHistory
from .serializers import *
from .clients import *
class OrderView(APIView):
    """
    API View to list all orders or create a new order.
    """
    def get(self, request, *args, **kwargs):
        auth_token = request.headers.get('AUTHORIZATION')

        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 10)
        total_pages = 0
        content = []

        user = get_user_info(auth_token)

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
            user = UserSerializer(data=user)
            for order in data.get('content'):
                order_items = get_order_items_by_order(order.get('id'))
                address = get_address_by_ward_id(auth_token, order.get('ward_id'), order.get('address'))
                payment_state = PaymentStateSerializer(data=get_payment_state(auth_token, order.get('payment_state_id')))
                payment_method = PaymentMethodSerializer(data=get_payment_method(auth_token, order.get('payment_method_id')))
                order_state = OrderStateSerializer(OrderState.objects.filter(order.get('order_state_id')))

                order_data = {
                    "id": order.get('id'),
                    "phone_number": order.get('phone_number'),
                    "created_at": order.get('created_at'),
                    "address": address.data,
                    "order_state": order_state.data,
                    "user": user.data,
                    "payment_method": payment_method.data,
                    "payment_state": payment_state.data,
                    "items": order_items,
                }

                content.append(OrderResponseSerializer(data=order_data))

        else:
            orders = Order.objects.all()
            total_pages = len(orders) + per_page // per_page
            start = (page - 1) * per_page
            end = start + per_page
            for order in orders[start:end]:
                order_items = get_order_items_by_order(order.get('id'))
                address = get_address_by_ward_id(auth_token, order.get('ward_id'), order.get('address'))
                payment_state = PaymentStateSerializer(data=get_payment_state(auth_token, order.get('payment_state_id')))
                payment_method = PaymentMethodSerializer(data=get_payment_method(auth_token, order.get('payment_method_id')))
                order_state = OrderStateSerializer(OrderState.objects.filter(order.get('order_state_id')))
                customer = get_user_by_id(auth_token, order.get('user_id'))
                order_data = {
                    "id": order.get('id'),
                    "phone_number": order.get('phone_number'),
                    "created_at": order.get('created_at'),
                    "address": address.data,
                    "order_state": order_state.data,
                    "user": customer.data,
                    "payment_method": payment_method.data,
                    "payment_state": payment_state.data,
                    "items": order_items,
                }

                content.append(OrderResponseSerializer(data=order_data))

        r = {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "content": content,
        }
        orderResponseSerializer = OrderResponseSerializer(data=r)
        return Response(orderResponseSerializer, status=status.HTTP_200_OK)

class OrderCreateAPIView(APIView):
    """
    API View to create a new order.
    """

    def post(self, request, *args, **kwargs):
        serializer = OrderRequestSerializer(data=request.data)
        if serializer.is_valid():
            auth_token = request.headers.get('AUTHORIZATION')
            user = get_user_info(auth_token)
            if not user or not user.get('id'):
                return Response({"detail": "Invalid user data"}, status=status.HTTP_400_BAD_REQUEST)
            
            payment_state_id = get_payment_state_by_name(auth_token, "Pending").get('id')
            Order.objects.create(
                user_id=user.get('id'),
                phone_number=serializer.validated_data['phone_number'],
                order_state=OrderState.objects.get(name="Pending"),
                ward_id=serializer.validated_data['address']['ward_id'],
                address=serializer.validated_data['address']['detail'],
                payment_method_id=payment_state_id,
                payment_state_id=serializer.validated_data['payment_method_id'],
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderRetrieveDestroyAPIView(APIView):
    """
    API View to retrieve or delete an order.
    """

    def get(self, request, *args, **kwargs):
        """
        Retrieve a specific order by ID.
        """
        auth_token = request.headers.get('AUTHORIZATION')
        user = get_user_info(auth_token)
        if not user:
            return Response({"detail": "Invalid user data"}, status=status.HTTP_400_BAD_REQUEST)

        order_id = self.kwargs.get('order_id') 
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        order_items = get_order_items_by_order(order.id)
        address = get_address_by_ward_id(auth_token, order.ward_id, order.address)
        payment_state = PaymentStateSerializer(data=get_payment_state(auth_token, order.payment_state_id))
        payment_method = PaymentMethodSerializer(data=get_payment_method(auth_token, order.payment_method_id))
        order_state = OrderStateSerializer(data=OrderState.objects.filter(order.order_state_id))
        customer = get_user_by_id(auth_token, order.user_id)

        if user.get('id') == order.user_id or user.get('role').get('name') == 'admin':
            order_data = {
                "id": order.id,
                "phone_number": order.phone_number,
                "created_at": order.created_at,
                "address": address.data,
                "order_state": order_state.data,
                "user": customer.data,
                "payment_method": payment_method.data,
                "payment_state": payment_state.data,
                "items": order_items,
            }
            return Response(OrderResponseSerializer(data=order_data).data)
        return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
    
class OrderCancelAPIView(APIView):
    """
    API View to cancel an order.
    """
    def post(self, request, *args, **kwargs):
        """
        Cancel an order by ID.
        """
        user = get_user_info(request.headers.get('AUTHORIZATION'))
        if not user:
            return Response({"detail": "Invalid user data"}, status=status.HTTP_400_BAD_REQUEST)
    
        order_id = self.kwargs.get('order_id')
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
    
        if user.get('id') == order.user_id or user.get('role').get('name') == 'admin':
            order.order_state = OrderState.objects.get(name="Cancelled")
            order.save()
            return Response({"detail": "Order cancelled successfully."}, status=status.HTTP_200_OK)
        return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

def get_orders_by_user(user_id, page, per_page):
    """
    Lấy danh sách đơn hàng của một người dùng cụ thể.
    
    Args:
        user_id (int): ID của người dùng.
        page (int): Số trang hiện tại.
        per_page (int): Số lượng đơn hàng trên mỗi trang.
        
    Returns:
        list: Danh sách đơn hàng của người dùng.
    """

    orders = Order.objects.filter(user_id=user_id)
    total_orders = orders.count()
    total_pages = total_orders + per_page // per_page  # Tính số trang
    start = (page - 1) * per_page
    end = start + per_page
    paginated_orders = orders[start:end]
    
    return {
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "content": paginated_orders,
    }

def get_order_items_by_order(order_id):
    """
    Lấy danh sách các sản phẩm trong một đơn hàng cụ thể.
    
    Args:
        order_id (int): ID của đơn hàng.
        
    Returns:
        list: Danh sách các sản phẩm trong đơn hàng.
    """
    order_items = OrderItem.objects.filter(order_id=order_id)
    result = []
    for item in order_items:
        product = get_product_by_id(item.product_id)
        result.append(OrderItemResponseSerializer(item, product=product))
    return result

def get_address_by_ward_id(token, ward_id, detail):
    """
    Lấy thông tin địa chỉ dựa trên ID địa chỉ.
    
    Args:
        address_id (int): ID của địa chỉ.
        detail (str): Thông tin chi tiết địa chỉ.
        
    Returns:
        dict: Thông tin địa chỉ nếu thành công.
        None: Nếu có lỗi xảy ra hoặc không tìm thấy địa chỉ.
    """

    ward = WardSerializer(data=get_address_by_ward(token, ward_id))
    address = {
        "ward": ward.data,
        "detail": detail,
    }
    return AddressSerializer(data=address)

def get_user_by_id(token, user_id):
    """
    Lấy thông tin người dùng dựa trên ID người dùng.
    
    Args:
        user_id (int): ID của người dùng.
        token (str): JWT hoặc access token của người dùng.
        
    Returns:
        dict: Thông tin người dùng nếu thành công.
        None: Nếu có lỗi xảy ra hoặc không tìm thấy người dùng.
    """

    c = get_user_info_by_user_id(token, user_id)
    return UserSerializer(data=c)