class Client:
    def __init__(self, name, age, password):
        self.name = name
        self.age = age
        self.password = password
        self.balance = 0

    def put_money(self, amount):
        if amount <= 0:
            return 'Cannot pay negative amount'
        self.balance += amount
        return 'Completed'

    def get_money(self, amount, password):
        if password != self.password:
            return 'Wrong password'
        if amount <= 0:
            return 'Wrong amount'
        if self.balance - amount < 0:
            return 'Not enough money'
        self.balance -= amount
        return 'Completed'

    def get_balance(self):
        return self.balance

    def change_age(self, new_age):
        self.age = new_age
        return 'Completed'

    def change_password(self, last_password, new_password):
        if last_password == self.password:
            self.password = new_password
            return 'Completed'
        return 'Wrong password'

    def change_name(self, new_name, password):
        if password == self.password:
            self.name = new_name
            return 'Completed'
        return 'Wrong password'


def transfer(client_1, client_2, amount, password):
    result = client_1.get_money(amount, password)
    if result != 'Completed':
        return result
    client_2.put_money(amount)
    return 'Completed'
