from enum import Enum

class PaymentStateEnum(Enum):
    PENDING = "Pending"
    PAID = "Paid"
    CANCELLED = "Cancelled"
    FAIL = "Fail"

class PaymentMethodEnum(Enum):
    CASH = "Cash"
    ONLINE = "Online"