from django.db import models

class PaymentState(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class PaymentMethod(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.CharField(max_length=50, unique=True)
    payment_state = models.ForeignKey(PaymentState, on_delete=models.SET_NULL, null=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Payment for Order {self.order_id}"