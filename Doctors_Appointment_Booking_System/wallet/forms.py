from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db import transaction as db_transaction
from django.db.models import F


class Wallet(models.Model):
    code = models.CharField(max_length=32, unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="wallet", 
        )
    balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.code}"

    def _validate_amount(self, amount: Decimal):
        try:
            amount = Decimal(amount)
        except (InvalidOperation, TypeError):
            raise ValueError("amount must be a valid decimal")
        if amount <= 0:
            raise ValueError("amount must be greater than 0")
        return amount

    def top_up(self, amount: Decimal):
        """Add funds (amount > 0) and create a DEPOSIT transaction atomically."""
        amount = self._validate_amount(amount)
        with db_transaction.atomic():
            Wallet.objects.filter(pk=self.pk).update(
                balance=F("balance") + amount
            )
            self.refresh_from_db(fields=["balance"])
            Transaction.objects.create(
                wallet=self, 
                payment_type="DEPOSIT", 
                amount=amount
            )
        return self.balance

    def deduct(self, amount: Decimal, cart=None):
        """Deduct funds (amount > 0) and create a PAYMENT transaction atomically."""
        amount = self._validate_amount(amount)
        with db_transaction.atomic():
            w = Wallet.objects.select_for_update().get(pk=self.pk)
            if w.balance < amount:
                raise ValueError("insufficient funds in wallet")
            w.balance = w.balance - amount
            w.save(update_fields=["balance"])
            Transaction.objects.create(
                wallet=w, 
                payment_type="PAYMENT", 
                amount=amount, 
                cart=cart
            )
            self.refresh_from_db(fields=["balance"])
        return self.balance


class Cart(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('CANCELED', 'Canceled'),
    ]
    pay_price = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    payment_status = models.CharField(
        max_length=16, 
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_STATUS_CHOICES[0][0]
    )
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
    wallet = models.ForeignKey(
        Wallet, 
        on_delete=models.PROTECT, 
        related_name="transactions"
    )
    payment_type = models.CharField(max_length=16, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.SET_NULL, 
        related_name="cart_transactions", 
        blank=True, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_type} {self.amount} for wallet {self.wallet_id}"