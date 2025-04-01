# Sử dụng image Python chính thức
FROM python:3.12

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép requirements.txt và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của User Service
COPY . .

# Thiết lập biến môi trường để chạy Django
ENV PYTHONUNBUFFERED=1

# Chạy migrations và khởi động server
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]