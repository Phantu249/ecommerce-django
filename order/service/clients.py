import httpx
import os
from .serializers import *
from django.conf import settings

def get_user_info(token: str):
    auth_service_url = f"{settings.USER_SERVICE_URL}/get_user_info"
    print(f"Auth service URL: {auth_service_url}")
    try:
        headers = {"Authorization": f"{token}", "Content-Type": "application/json", "Cross-Service": "order-service"}
        response = httpx.get(auth_service_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        print(f"Error: Received status code {response.status_code} - {response.text}")
        return None
    except httpx.RequestError as e:
        print(f"Request failed: {e}")
        return None

def get_user_info_by_user_id(token: str, user_id: int):
    auth_service_url = f"{settings.USER_SERVICE_URL}/{user_id}"
    try:
        headers = {"Authorization": f"{token}", "Content-Type": "application/json", "Cross-Service": "order-service"}
        response = httpx.get(auth_service_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        print(f"Error: Received status code {response.status_code} - {response.text}")
        return None
    except httpx.RequestError as e:
        print(f"Request failed: {e}")
        return None

def get_product_by_id(product_id):
    product_service_url = f"{settings.PRODUCT_SERVICE_URL}/{product_id}?detail=true"
    try:
        response = httpx.get(product_service_url)
        if response.status_code == 200:
            return response.json()
        print(f"Error: Received status code {response.status_code} - {response.text}")
        return None
    except httpx.RequestError as e:
        print(f"Request failed: {e}")
        return None

def get_payment_state(auth_token, payment_state_id):
    payment_service_url = f"http://localhost:8087/api/payment/{payment_state_id}"
    try:
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        response = httpx.get(payment_service_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        print(f"Error: Received status code {response.status_code} - {response.text}")
        return None
    except httpx.RequestError as e:
        print(f"Request failed: {e}")
        return None

def get_payment_method(auth_token, payment_method_id):
    payment_service_url = f"http://localhost:8087/api/payment/method/{payment_method_id}"
    try:
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        response = httpx.get(payment_service_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        print(f"Error: Received status code {response.status_code} - {response.text}")
        return None
    except httpx.RequestError as e:
        print(f"Request failed: {e}")
        return None

def get_payment_state_by_name(auth_token, payment_state_name):
    payment_service_url = f"http://localhost:8087/api/payment/state?name={payment_state_name}"
    try:
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        response = httpx.get(payment_service_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        print(f"Error: Received status code {response.status_code} - {response.text}")
        return None
    except httpx.RequestError as e:
        print(f"Request failed: {e}")
        return None

def get_address_by_ward(auth_token, ward_id):
    address_service_url = f"{settings.USER_SERVICE_URL}/address/ward/{ward_id}"
    try:
        headers = {"Authorization": f"{auth_token}", "Content-Type": "application/json", "Cross-Service": "order-service"}
        response = httpx.get(address_service_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        print(f"Error: Received status code {response.status_code} - {response.text}")
        return None
    except httpx.RequestError as e:
        print(f"Request failed: {e}")
        return None

def get_orders_by_user(user_id, page, per_page):
    orders = Order.objects.filter(user_id=user_id)
    total_orders = orders.count()
    total_pages = (total_orders + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_orders = [
        {
            "id": order.id,
            "phone_number": order.phone_number,
            "created_at": order.created_at,
            "ward_id": order.ward_id,
            "address": order.address,
            "order_state_id": order.order_state_id,
            "payment_state_id": order.payment_state_id,
            "payment_method_id": order.payment_method_id,
        }
        for order in orders[start:end]
    ]
    return {
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "content": paginated_orders,
    }

def get_order_items_by_order(order_id):
    order_items = OrderItem.objects.filter(order_id=order_id)
    return [OrderItemResponseSerializer(item).data for item in order_items]

def get_address_by_ward_id(token, ward_id, detail):
    ward_data = get_address_by_ward(token, ward_id)
    ward_serializer = WardSerializer(data=ward_data)
    if ward_serializer.is_valid():
        address = {"ward": ward_serializer.data, "detail": detail}
        address_serializer = AddressSerializer(data=address)
        if address_serializer.is_valid():
            return address_serializer
    return AddressSerializer(data={})

def get_user_by_id(token, user_id):
    user_data = get_user_info_by_user_id(token, user_id)
    user_serializer = UserSerializer(data=user_data)
    if user_serializer.is_valid():
        return user_serializer
    return UserSerializer(data={})