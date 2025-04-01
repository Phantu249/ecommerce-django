from django.http import JsonResponse
import httpx

def get_user_info(token: str):
    """
    Lấy thông tin người dùng từ request bằng cách gọi API xác thực.
    
    Args:
        token (str): JWT hoặc access token của người dùng.
        
    Returns:
        dict: Thông tin người dùng nếu thành công.
        None: Nếu có lỗi xảy ra hoặc token không hợp lệ.
    """
    # Định nghĩa URL của dịch vụ xác thực
    auth_service_url = "http:localhost:8088//api/user/get-user-info"
    
    try:
        # Tạo header với token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Cross-Service": "order-service",
        }
        
        # Gửi yêu cầu GET đến dịch vụ xác thực
        response = httpx.get(auth_service_url, headers=headers)
        
        # Kiểm tra mã trạng thái HTTP
        if response.status_code == 200:
            # Trả về dữ liệu JSON nếu thành công
            return response.json()
        elif response.status_code == 401:
            # Trường hợp token không hợp lệ
            print("Unauthorized: Invalid or expired token.")
            return None
        else:
            # Trường hợp lỗi khác từ server
            print(f"Error: Received status code {response.status_code} - {response.text}")
            return None

    except httpx.RequestError as e:
        # Xử lý lỗi kết nối (network error)
        print(f"Request failed: {e}")
        return None
    
def get_user_info_by_user_id(token: str, user_id: int):
    """
    Lấy thông tin người dùng từ dịch vụ xác thực dựa trên ID người dùng.
    
    Args:
        token (str): JWT hoặc access token của người dùng.
        user_id (int): ID của người dùng.
        
    Returns:
        dict: Thông tin người dùng nếu thành công.
        None: Nếu có lỗi xảy ra hoặc không tìm thấy người dùng.
    """
    # Định nghĩa URL của dịch vụ xác thực
    auth_service_url = f"http://localhost:8088/api/user/{user_id}"
    
    try:
        # Tạo header với token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Cors-Service": "order-service",
        }
        
        # Gửi yêu cầu GET đến dịch vụ xác thực
        response = httpx.get(auth_service_url, headers=headers)
        
        # Kiểm tra mã trạng thái HTTP
        if response.status_code == 200:
            # Trả về dữ liệu JSON nếu thành công
            return response.json()
        elif response.status_code == 404:
            # Trường hợp không tìm thấy người dùng
            print("User not found.")
            return None
        else:
            # Trường hợp lỗi khác từ server
            print(f"Error: Received status code {response.status_code} - {response.text}")
            return None

    except httpx.RequestError as e:
        # Xử lý lỗi kết nối (network error)
        print(f"Request failed: {e}")
        return None
    
def get_product_by_id(product_id):
    """
    Lấy thông tin sản phẩm từ dịch vụ sản phẩm dựa trên ID sản phẩm.
    
    Args:
        product_id (int): ID của sản phẩm.
        
    Returns:
        dict: Thông tin sản phẩm nếu thành công.
        None: Nếu có lỗi xảy ra hoặc không tìm thấy sản phẩm.
    """
    # Định nghĩa URL của dịch vụ sản phẩm
    product_service_url = f"http://localhost:8089/api/product/{product_id}?detail=true"
    
    try:
        # Gửi yêu cầu GET đến dịch vụ sản phẩm
        response = httpx.get(product_service_url)
        
        # Kiểm tra mã trạng thái HTTP
        if response.status_code == 200:
            # Trả về dữ liệu JSON nếu thành công
            return response.json()
        elif response.status_code == 404:
            # Trường hợp không tìm thấy sản phẩm
            print("Product not found.")
            return None
        else:
            # Trường hợp lỗi khác từ server
            print(f"Error: Received status code {response.status_code} - {response.text}")
            return None

    except httpx.RequestError as e:
        # Xử lý lỗi kết nối (network error)
        print(f"Request failed: {e}")
        return None
    
def get_payment_state(auth_token, payment_state_id):
    """
    Lấy thông tin trạng thái thanh toán từ dịch vụ thanh toán dựa trên ID trạng thái.
    
    Args:
        payment_state_id (int): ID của trạng thái thanh toán.
        auth_token (str): JWT hoặc access token của người dùng.
        
    Returns:
        dict: Thông tin trạng thái thanh toán nếu thành công.
        None: Nếu có lỗi xảy ra hoặc không tìm thấy trạng thái thanh toán.
    """
    # Định nghĩa URL của dịch vụ thanh toán
    payment_service_url = f"http://localhost:8087/api/payment/{payment_state_id}"
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }
        # Gửi yêu cầu GET đến dịch vụ thanh toán
        response = httpx.get(payment_service_url, headers=headers)
        
        # Kiểm tra mã trạng thái HTTP
        if response.status_code == 200:
            # Trả về dữ liệu JSON nếu thành công
            return response.json()
        elif response.status_code == 404:
            # Trường hợp không tìm thấy trạng thái thanh toán
            print("Payment state not found.")
            return None
        else:
            # Trường hợp lỗi khác từ server
            print(f"Error: Received status code {response.status_code} - {response.text}")
            return None

    except httpx.RequestError as e:
        # Xử lý lỗi kết nối (network error)
        print(f"Request failed: {e}")
        return None
    
def get_payment_method(auth_token, payment_method_id):
    """
    Lấy thông tin phương thức thanh toán từ dịch vụ thanh toán dựa trên ID phương thức.
    
    Args:
        auth_token (str): JWT hoặc access token của người dùng.
        payment_method_id (int): ID của phương thức thanh toán.
        
    Returns:
        dict: Thông tin phương thức thanh toán nếu thành công.
        None: Nếu có lỗi xảy ra hoặc không tìm thấy phương thức thanh toán.
    """
    # Định nghĩa URL của dịch vụ thanh toán
    payment_service_url = f"http://localhost:8087/api/payment/method/{payment_method_id}"
    
    try:
        # Tạo header với token
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }
        
        # Gửi yêu cầu GET đến dịch vụ thanh toán
        response = httpx.get(payment_service_url, headers=headers)
        
        # Kiểm tra mã trạng thái HTTP
        if response.status_code == 200:
            # Trả về dữ liệu JSON nếu thành công
            return response.json()
        elif response.status_code == 404:
            # Trường hợp không tìm thấy phương thức thanh toán
            print("Payment method not found.")
            return None
        else:
            # Trường hợp lỗi khác từ server
            print(f"Error: Received status code {response.status_code} - {response.text}")
            return None

    except httpx.RequestError as e:
        # Xử lý lỗi kết nối (network error)
        print(f"Request failed: {e}")
        return None
    
def get_payment_state_by_name(auth_token, payment_state_name):
    """
    Lấy thông tin trạng thái thanh toán từ dịch vụ thanh toán dựa trên ID phương thức.
    
    Args:
        auth_token (str): JWT hoặc access token của người dùng.
    Returns:
        dict: Thông tin phương thức thanh toán nếu thành công.
        None: Nếu có lỗi xảy ra hoặc không tìm thấy phương thức thanh toán.
    """
    # Định nghĩa URL của dịch vụ thanh toán
    payment_service_url = f"http://localhost:8087/api/payment/state?name={payment_state_name}"

    
    try:
        # Gửi yêu cầu GET đến dịch vụ thanh toán
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }

        response = httpx.get(payment_service_url, headers=headers)
        
        # Kiểm tra mã trạng thái HTTP
        if response.status_code == 200:
            # Trả về dữ liệu JSON nếu thành công
            return response.json()
        elif response.status_code == 404:
            # Trường hợp không tìm thấy phương thức thanh toán
            print("Payment method not found.")
            return None
        else:
            # Trường hợp lỗi khác từ server
            print(f"Error: Received status code {response.status_code} - {response.text}")
            return None

    except httpx.RequestError as e:
        # Xử lý lỗi kết nối (network error)
        print(f"Request failed: {e}")
        return None
    
def get_address_by_ward(auth_token, ward_id):
    """
    Lấy thông tin địa chỉ từ dịch vụ địa chỉ dựa trên ID ward.
    
    Args:
        ward_id (int): ID của ward.
        auth_token (str): JWT hoặc access token của người dùng.
        
    Returns:
        dict: Thông tin địa chỉ nếu thành công.
        None: Nếu có lỗi xảy ra hoặc không tìm thấy địa chỉ.
    """
    # Định nghĩa URL của dịch vụ địa chỉ
    address_service_url = f"http://localhost:8086/api/user/address/ward/{ward_id}"
    
    try:
        # Tạo header với token
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }
        # Gửi yêu cầu GET đến dịch vụ địa chỉ
        response = httpx.get(address_service_url, headers=headers)
        
        # Kiểm tra mã trạng thái HTTP
        if response.status_code == 200:
            # Trả về dữ liệu JSON nếu thành công
            return response.json()
        elif response.status_code == 404:
            # Trường hợp không tìm thấy địa chỉ
            print("Address not found.")
            return None
        else:
            # Trường hợp lỗi khác từ server
            print(f"Error: Received status code {response.status_code} - {response.text}")
            return None

    except httpx.RequestError as e:
        # Xử lý lỗi kết nối (network error)
        print(f"Request failed: {e}")
        return None