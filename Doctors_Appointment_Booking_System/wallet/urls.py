from django.urls import path
from .views import wallet_top_up, wallet_deduct, wallet_balance, wallet_transactions

app_name = 'wallet'

urlpatterns = [
    path("top-up/", wallet_top_up, name="top_up"),
    path("deduct/", wallet_deduct, name="deduct"),
    path("balance/", wallet_balance, name="balance"),
    path("transactions/", wallet_transactions, name="transactions"),
]