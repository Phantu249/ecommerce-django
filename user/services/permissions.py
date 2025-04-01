# your_app/permissions.py
from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name == 'ADMIN'

class IsCustomRole(permissions.BasePermission):
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name in self.allowed_roles

class IsCrossServiceCall(permissions.BasePermission):
    """
    Custom permission để cho phép truy cập nếu request có header 'Cross-Service'.
    """

    def has_permission(self, request, view):
        # Lấy giá trị của header "SERVICE_AUTH"
        service_auth = request.headers.get("Cross-Service")
        # Kiểm tra xem header có tồn tại và không rỗng
        return bool(service_auth)