from django.contrib import admin

from .models import Wallet, Cart, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'code', 'balance', 'created_at', 'updated_at')
    search_fields = ('user__username', 'code')
    list_filter = ('created_at', 'updated_at')
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'pay_price', 'payment_status', 'support_code', 'created_at', 'updated_at')
    search_fields = ('support_code', )
    list_filter = ('payment_status', 'created_at', 'updated_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'payment_type', 'amount', 'cart', 'created_at')
    search_fields = ('wallet__user__username', 'cart__id')
    list_filter = ('payment_type', 'created_at')