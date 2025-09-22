from django.test import TestCase
from django.utils.crypto import get_random_string

from account.models import User
from .models import Wallet, Transaction


class WalletTestCase(TestCase):
    def setUp(self):
        user = User.objects.create()
        code = get_random_string(32)
        Wallet.objects.create(code=code, user=user)

    def test_wallet_can_change(self):
        wallet = Wallet.objects.first()
        self.assertRaisesMessage(ValueError, 'amount must be a valid decimal', wallet.top_up, 'amount')
        self.assertRaisesMessage(ValueError, 'amount must be greater than 0', wallet.deduct, -10)
        wallet.top_up(100)
        self.assertEqual(wallet.balance, 100)
        self.assertRaisesMessage(ValueError, 'insufficient funds in wallet', wallet.deduct, 200)
        wallet.deduct(50)
        self.assertEqual(wallet.balance, 50)
        self.assertEqual(Transaction.objects.count(), 2)
        self.assertEqual(Transaction.objects.first().payment_type, 'DEPOSIT')
