from django.urls import path
from wallet.views import *

app_name = 'wallet'

urlpatterns = [
    # page views
    path('', index_page, name='index'),
    path('top_up/page', top_up_page, name='top_up_page'),
    path('transactions/page', transactions_page, name='transactions_page'),

    # json api
    path("top-up/", wallet_top_up, name="top_up"),
    path("deduct/", wallet_deduct, name="deduct"),
    path("balance/", wallet_balance, name="balance"),
    path("transactions/", wallet_transactions, name="transactions"),
]