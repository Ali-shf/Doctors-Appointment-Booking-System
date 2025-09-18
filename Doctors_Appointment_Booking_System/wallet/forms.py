from django import forms
from wallet.views import *


class WalletTopUpForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=14,
        decimal_places=2,
        min_value=1,
        label='Amount to add',
        help_text='Enter the amount you want to top up'
    )