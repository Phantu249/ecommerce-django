from django.urls import path
from . import views

urlpatterns = [
    path('product/<int:id>', views.ProductDetailView.as_view(), name='product-detail'),
    path('product', views.ProductListView.as_view(), name='product-list'),
    path('product/category', views.CategoryListView.as_view(), name='category-list'),
    path('product/category/<int:id>', views.CategoryDetailView.as_view(), name='category-detail'),
    path('product/<int:id>/stock', views.ProductStockView.as_view(), name='product-stock'),
    path('product/stock', views.ProductChangeStockView.as_view(), name='product-stock-change'),
]