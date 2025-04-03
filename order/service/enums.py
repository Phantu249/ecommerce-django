from enum import Enum

class OrderStateEnum(Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    SHIPPING = "Shipping"
    CANCELLED = "Cancelled"
    DISAPPROVED = "Disapproved"
    DONE = "Done"

class PaymentStateEnum(Enum):
    PENDING = "Pending"
    PAID = "Paid"
    CANCELLED = "Cancelled"
    FAIL = "Fail"

class PaymentMethodEnum(Enum):
    CASH = "Cash"
    ONLINE = "Online"