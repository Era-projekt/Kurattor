from flask import Flask
from firebase_config import init_firebase

# Инициализация Firebase при старте
init_firebase()

app = Flask(__name__)
# Секретный ключ для сессий
app.secret_key = 'super_secret_kuraton_key_123'

# Регистрация маршрутов
from routes import init_routes
init_routes(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
