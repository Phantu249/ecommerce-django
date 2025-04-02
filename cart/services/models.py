from django.db import models

class Cart(models.Model):
    id = models.IntegerField(primary_key=True)  # Khớp với user_id từ User Service

    def __str__(self):
        return f"Cart {self.id}"

class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        return f"Item {self.product_id} in Cart {self.cart.id}"