from datetime import datetime
from flask import Flask, jsonify, render_template, request, session
from modules.bank_module import Client, transfer

app = Flask(__name__)
data = {}
history = {}

MESSAGES = {
    'Cannot pay negative amount': 'Сумма должна быть больше нуля',
    'Wrong amount': 'Сумма должна быть больше нуля',
    'Not enough money': 'Недостаточно средств',
    'Wrong password': 'Неверный пароль',
}


def fail(text, code=400):
    return jsonify(ok=False, error=MESSAGES.get(text, text)), code


def current():
    return data.get(session.get('name'))


def log(name, title, amount):
    history.setdefault(name, []).insert(0, {
        'title': title, 'amount': amount,
        'time': datetime.now().strftime('%d.%m %H:%M')})


def profile(client):
    return jsonify(ok=True, name=client.name, age=client.age,
                   balance=client.get_balance(),
                   history=history.get(client.name, [])[:10])


def get_amount(body):
    try:
        return round(float(body.get('amount')), 2)
    except (TypeError, ValueError):
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/register', methods=['POST'])
def register():
    b = request.get_json(silent=True) or {}
    name = str(b.get('name', '')).strip()
    password = str(b.get('password', ''))
    try:
        age = int(b.get('age'))
    except (TypeError, ValueError):
        return fail('Укажите возраст числом')
    if not name or len(password) < 4:
        return fail('Введите имя и пароль от 4 символов')
    if age < 18:
        return fail('Открыть счёт можно с 18 лет')
    if name in data:
        return fail('Клиент с таким именем уже есть', 409)
    data[name] = Client(name, age, password)
    session['name'] = name
    return profile(data[name])


@app.route('/api/login', methods=['POST'])
def login():
    b = request.get_json(silent=True) or {}
    client = data.get(str(b.get('name', '')).strip())
    if not client or client.password != b.get('password'):
        return fail('Неверное имя или пароль', 401)
    session['name'] = client.name
    return profile(client)


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify(ok=True)


@app.route('/api/me')
def me():
    client = current()
    return profile(client) if client else fail('Не авторизован', 401)


@app.route('/api/deposit', methods=['POST'])
def deposit():
    client = current()
    if not client:
        return fail('Не авторизован', 401)
    amount = get_amount(request.get_json(silent=True) or {})
    if amount is None:
        return fail('Введите сумму')
    result = client.put_money(amount)
    if result != 'Completed':
        return fail(result)
    log(client.name, 'Пополнение', amount)
    return profile(client)


@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    client = current()
    if not client:
        return fail('Не авторизован', 401)
    b = request.get_json(silent=True) or {}
    amount = get_amount(b)
    if amount is None:
        return fail('Введите сумму')
    result = client.get_money(amount, b.get('password'))
    if result != 'Completed':
        return fail(result)
    log(client.name, 'Снятие наличных', -amount)
    return profile(client)


@app.route('/api/transfer', methods=['POST'])
def make_transfer():
    client = current()
    if not client:
        return fail('Не авторизован', 401)
    b = request.get_json(silent=True) or {}
    amount = get_amount(b)
    to = data.get(str(b.get('to', '')).strip())
    if amount is None:
        return fail('Введите сумму')
    if not to:
        return fail('Получатель не найден', 404)
    if to is client:
        return fail('Нельзя переводить самому себе')
    result = transfer(client, to, amount, b.get('password'))
    if result != 'Completed':
        return fail(result)
    log(client.name, 'Перевод: ' + to.name, -amount)
    log(to.name, 'Перевод от ' + client.name, amount)
    return profile(client)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
