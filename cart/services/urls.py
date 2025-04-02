from django.urls import path
from . import views

urlpatterns = [
    path('cart', views.CartView.as_view(), name='cart'),
    path('cart/<int:product_id>', views.CartItemDeleteView.as_view(), name='cart-item-delete'),
    path('cart/to-order', views.CartToOrderView.as_view(), name='cart-to-order'),
]