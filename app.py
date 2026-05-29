from flask import Flask
import os
from firebase_config import init_firebase

# Инициализация Firebase при старте
init_firebase()

app = Flask(__name__, static_folder='static')
# Секретный ключ для сессий
app.secret_key = 'super_secret_kuraton_key_123'
# Allow up to 32MB file uploads
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

# Ensure the uploads directory exists at startup
uploads_dir = os.path.join(app.static_folder, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)

# Регистрация маршрутов
from routes import init_routes
init_routes(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
