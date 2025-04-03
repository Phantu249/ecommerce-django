from django.urls import path
from django.http import HttpResponse
from .views import (
    PaymentAPIView, PaymentCreateAPIView, PaymentStateListAPIView,
    PaymentMethodListAPIView, PaymentMethodDetailAPIView
)

def test_view(request):
    return HttpResponse("Test view for payment service.")

urlpatterns = [
    path('payments/<str:order_id>', PaymentAPIView.as_view(), name='payment-detail'),
    path('payment', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('payment/state', PaymentStateListAPIView.as_view(), name='payment-state-list'),
    path('payment/method', PaymentMethodListAPIView.as_view(), name='payment-method-list'),
    path('payment/method/<int:id>', PaymentMethodDetailAPIView.as_view(), name='payment-method-detail'),
    path('test/', test_view, name='test-view'),  # Test view
]