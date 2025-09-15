from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

from decimal import Decimal


class PaymentType(models.TextChoices):
    DEPOSIT = "DEPOSIT", "Deposit / Top-up"
    WITHDRAW = "WITHDRAW", "Withdraw"
    PAYMENT = "PAYMENT", "Service Payment"
    REFUND = "REFUND", "Refund"


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PAID = "PAID", "Paid"
    FAILED = "FAILED", "Failed"
    CANCELED = "CANCELED", "Canceled"


class Wallet(models.Model):
    code = models.CharField(max_length=32, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet",
                                db_index=True)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"),
                                  validators=[MinValueValidator(Decimal("0.00"))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.code}"


class Cart(models.Model):
    visit = models.OneToOneField("reservation.Visit", on_delete=models.PROTECT, related_name="cart", db_index=True)
    pay_price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    payment_status = models.CharField(max_length=16, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    support_code = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["payment_status"]),
        ]

    def __str__(self):
        return f"Cart #{self.id} for visit #{self.visit_id}"


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="transactions", db_index=True)
    payment_type = models.CharField(max_length=16, choices=PaymentType.choices)
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, related_name="transactions", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["payment_type"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.payment_type} {self.amount} for wallet {self.wallet_id}"
