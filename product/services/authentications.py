import requests
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class UserServiceAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None  # Không có token, bỏ qua xác thực

        # Gọi sang user microservice để xác thực token
        user_service_url = settings.USER_SERVICE_URL + "/get-user-info"
        try:
            response = requests.get(
                user_service_url,
                headers={"Authorization": auth_header},
                timeout=5  # Thêm timeout để tránh treo request
            )
            response.raise_for_status()  # Ném lỗi nếu không phải 200
        except requests.RequestException as e:
            raise AuthenticationFailed(f"Lỗi khi xác thực token: {str(e)}")

        user_data = response.json()  # Lấy thông tin user từ response

        # Kiểm tra dữ liệu trả về có hợp lệ không
        if not user_data or "id" not in user_data:
            raise AuthenticationFailed("Dữ liệu user không hợp lệ")

        return (user_data, None)  # Trả về user_data như một dict