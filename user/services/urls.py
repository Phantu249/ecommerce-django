from django.urls import path
from .views import LoginView, RegisterView, GetUserInfoView, UpdateUserInfoView, GetWardsView, GetDistrictsView, GetCitiesView, AddAddressView

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('register', RegisterView.as_view(), name='register'),
    path('get-user-info', GetUserInfoView.as_view(), name='get_user_info'),
    path('update-info', UpdateUserInfoView.as_view(), name='update_user_info'),
    path('address/ward', GetWardsView.as_view(), name='get_wards'),
    path('address/district', GetDistrictsView.as_view(), name='get_districts'),
    path('address/city', GetCitiesView.as_view(), name='get_cities'),
    path('address', AddAddressView.as_view(), name='add_address'),
]