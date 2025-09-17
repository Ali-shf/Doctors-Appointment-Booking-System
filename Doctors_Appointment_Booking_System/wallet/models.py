from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal



class Wallet(models.Model):
    code = models.CharField(max_length=32, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet",)
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
    

    def top_up(self, amount: Decimal):
        ''' Add funds to the wallet and create a deposit transaction '''
        amount = Decimal(amount)
        self.balance += amount
        self.save()
        Transaction.objects.create(
            wallet=self,
            payment_type='DEPOSIT',
            amount=amount
        )
        return self.balance
    

    def deduct(self, amount: Decimal, cart=None):
        ''' Deduct funds from the wallet and create a payment transaction '''
        amount = Decimal(amount)
        if self.balance < amount:
            raise ValueError('Insufficient funds in wallet')
        self.balance -= amount
        self.save()
        Transaction.objects.create(
            wallet=self,
            payment_type='PAYMENT',
            amount=amount,
            cart=cart, # Link to the cart if provided
        )
        return self.balance
    



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
