# your_app/permissions.py
from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions

class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user != AnonymousUser())

class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        if not IsAuth().has_permission(request, view):
            return False
        role = request.user.get('role', {})
        return role.get('name') == 'ADMIN'

class IsAuthOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return IsAuth().has_permission(request, view) or IsAdminRole().has_permission(request, view)


class IsCustomRole(permissions.BasePermission):
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        if not request.user or request.user == AnonymousUser():
            return False
        role = request.user.get('role', {})
        return role.get('name') in self.allowed_roles

class IsCrossServiceCall(permissions.BasePermission):
    """
    Custom permission để cho phép truy cập nếu request có header 'Cross-Service'.
    """

    def has_permission(self, request, view):
        # Lấy giá trị của header "SERVICE_AUTH"
        service_auth = request.headers.get("Cross-Service")
        # Kiểm tra xem header có tồn tại và không rỗng
        return bool(service_auth)