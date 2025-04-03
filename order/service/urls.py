from django.urls import path, include
from .views import OrderView, OrderCreateAPIView, OrderRetrieveDestroyAPIView, OrderCancelAPIView, OrderStateHistoryView

urlpatterns = [
    path('orders/', OrderView.as_view(), name='order-list'),
    path('orders/create', OrderCreateAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderRetrieveDestroyAPIView.as_view(), name='order-detail'),
    path('orders/<int:pk>/cancel', OrderCancelAPIView.as_view(), name='order-cancel'),
    path('orders/state/<int:pk>', OrderStateHistoryView.as_view(), name='order-state-history')
]