from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

from decimal import Decimal





class Wallet(models.Model):
    code = models.CharField(max_length=32, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet",)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"),
                                  validators=[MinValueValidator(Decimal("0.00"))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.code}"


class Cart(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('CANCELED', 'Canceled'),
    ]
    pay_price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    payment_status = models.CharField(max_length=16, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_CHOICES[0][0])
    support_code = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Cart #{self.id}"


class Transaction(models.Model): 
    PAYMENT_TYPE_CHOICES = [
        ('DEPOSIT', 'Deposit / Top-up'),
        ('WITHDRAW', 'Withdraw'),
        ('PAYMENT', 'Service Payment'),
        ('REFUND', 'Refund'),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="transactions")
    payment_type = models.CharField(max_length=16, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, related_name="cart_transactions", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.payment_type} {self.amount} for wallet {self.wallet_id}"
