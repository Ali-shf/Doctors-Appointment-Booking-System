from django.contrib import admin

from .models import Wallet, Cart, Transaction

admin.site.register(Wallet)

admin.site.register(Cart)

admin.site.register(Transaction)
