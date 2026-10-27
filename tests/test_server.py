import unittest

import app as vbank


class ApiTests(unittest.TestCase):
    def setUp(self):
        vbank.data.clear()
        vbank.history.clear()
        self.http = vbank.app.test_client()

    def register(self, client, name='anna', password='1234', age=20):
        return client.post('/api/register',
                           json={'name': name, 'age': age, 'password': password})

    def test_register_ok(self):
        res = self.register(self.http)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['ok'])
        self.assertEqual(res.json['balance'], 0)

    def test_register_under_18(self):
        res = self.register(self.http, age=17)
        self.assertFalse(res.json['ok'])

    def test_register_duplicate_name(self):
        self.register(self.http)
        res = self.register(vbank.app.test_client())
        self.assertEqual(res.status_code, 409)

    def test_login_wrong_password(self):
        self.register(self.http)
        res = vbank.app.test_client().post(
            '/api/login', json={'name': 'anna', 'password': 'bad'})
        self.assertEqual(res.status_code, 401)

    def test_deposit_requires_login(self):
        res = self.http.post('/api/deposit', json={'amount': 10})
        self.assertEqual(res.status_code, 401)

    def test_deposit_and_history(self):
        self.register(self.http)
        res = self.http.post('/api/deposit', json={'amount': 100})
        self.assertEqual(res.json['balance'], 100)
        self.assertEqual(res.json['history'][0]['title'], 'Пополнение')

    def test_withdraw_not_enough_money(self):
        self.register(self.http)
        res = self.http.post('/api/withdraw', json={'amount': 5, 'password': '1234'})
        self.assertEqual(res.json['error'], 'Недостаточно средств')

    def test_transfer_between_clients(self):
        self.register(self.http, 'anna', '1234')
        other = vbank.app.test_client()
        self.register(other, 'boris', '5678')
        self.http.post('/api/deposit', json={'amount': 100})

        res = self.http.post('/api/transfer',
                             json={'to': 'boris', 'amount': 40, 'password': '1234'})
        self.assertEqual(res.json['balance'], 60)
        self.assertEqual(other.get('/api/me').json['balance'], 40)

    def test_transfer_to_unknown_client(self):
        self.register(self.http)
        res = self.http.post('/api/transfer',
                             json={'to': 'nobody', 'amount': 1, 'password': '1234'})
        self.assertEqual(res.status_code, 404)

    def test_transfer_to_self(self):
        self.register(self.http)
        res = self.http.post('/api/transfer',
                             json={'to': 'anna', 'amount': 1, 'password': '1234'})
        self.assertFalse(res.json['ok'])


if __name__ == '__main__':
    unittest.main()
