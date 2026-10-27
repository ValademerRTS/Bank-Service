import unittest

from modules.bank_module import Client, transfer


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.client = Client('Anna', 25, '1234')

    def test_new_client_has_zero_balance(self):
        self.assertEqual(self.client.get_balance(), 0)

    def test_put_money_increases_balance(self):
        self.assertEqual(self.client.put_money(100), 'Completed')
        self.assertEqual(self.client.get_balance(), 100)

    def test_put_negative_amount_is_rejected(self):
        self.assertEqual(self.client.put_money(-5), 'Cannot pay negative amount')
        self.assertEqual(self.client.get_balance(), 0)

    def test_get_money_with_right_password(self):
        self.client.put_money(100)
        self.assertEqual(self.client.get_money(30, '1234'), 'Completed')
        self.assertEqual(self.client.get_balance(), 70)

    def test_get_money_with_wrong_password(self):
        self.client.put_money(100)
        self.assertEqual(self.client.get_money(30, 'bad'), 'Wrong password')
        self.assertEqual(self.client.get_balance(), 100)

    def test_get_money_more_than_balance(self):
        self.client.put_money(10)
        self.assertEqual(self.client.get_money(50, '1234'), 'Not enough money')

    def test_get_negative_amount_is_rejected(self):
        self.assertEqual(self.client.get_money(-100, '1234'), 'Wrong amount')
        self.assertEqual(self.client.get_balance(), 0)

    def test_change_password(self):
        self.assertEqual(self.client.change_password('bad', 'new'), 'Wrong password')
        self.assertEqual(self.client.change_password('1234', 'new'), 'Completed')
        self.assertEqual(self.client.password, 'new')


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.client_1 = Client('Anna', 25, '125534')
        self.client_2 = Client('Vadim', 35, '555124')
        self.client_1.put_money(10000)

    def test_transfer(self):
        result = transfer(self.client_1, self.client_2, 2000, '125534')
        self.assertEqual(result, 'Completed')
        self.assertEqual(self.client_1.get_balance(), 8000)
        self.assertEqual(self.client_2.get_balance(), 2000)

    def test_transfer_wrong_password_changes_nothing(self):
        result = transfer(self.client_1, self.client_2, 40, 'pb')
        self.assertEqual(result, 'Wrong password')
        self.assertEqual(self.client_1.get_balance(), 10000)
        self.assertEqual(self.client_2.get_balance(), 0)

    def test_transfer_not_enough_money(self):
        result = transfer(self.client_1, self.client_2, 50000, '125534')
        self.assertEqual(result, 'Not enough money')
        self.assertEqual(self.client_1.get_balance(), 10000)
        self.assertEqual(self.client_2.get_balance(), 0)


if __name__ == '__main__':
    unittest.main()