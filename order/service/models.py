from django.db import models

from django.db import models

class OrderState(models.Model):
    """
    Trạng thái của đơn hàng (ví dụ: Pending, Processing, Shipped, Delivered, Cancelled).
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    Thông tin đơn hàng.
    """
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=False, blank=False, verbose_name="User ID")
    phone_number = models.CharField(max_length=10, null=False, blank=False, verbose_name="Phone Number")
    order_state = models.ForeignKey(
        OrderState, 
        on_delete=models.CASCADE, 
        null=False, 
        blank=False, 
        related_name="orders", 
        verbose_name="Order State"
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False, verbose_name="Created At")
    ward_id = models.IntegerField(null=False, blank=False, verbose_name="Ward ID")
    address = models.CharField(max_length=255, null=False, blank=False, verbose_name="Address")

    def __str__(self):
        return f"Order {self.id} by User {self.user_id}"


class OrderItem(models.Model):
    """
    Chi tiết sản phẩm trong đơn hàng.
    """
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        null=False, 
        blank=False, 
        related_name="items", 
        verbose_name="Order"
    )
    product_id = models.IntegerField(null=False, blank=False, verbose_name="Product ID")
    quantity = models.IntegerField(null=False, blank=False, verbose_name="Quantity")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, verbose_name="Price")

    def __str__(self):
        return f"{self.quantity} x Product {self.product_id} in Order {self.order.id}"


class OrderStateHistory(models.Model):
    """
    Lịch sử trạng thái của đơn hàng.
    """
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        null=False, 
        blank=False, 
        related_name="state_history", 
        verbose_name="Order"
    )
    order_state = models.ForeignKey(
        OrderState, 
        on_delete=models.CASCADE, 
        null=False, 
        blank=False, 
        related_name="state_history", 
        verbose_name="Order State"
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False, verbose_name="Created At")

    def __str__(self):
        return f"Order {self.order.id} changed to {self.order_state.name} at {self.created_at}"