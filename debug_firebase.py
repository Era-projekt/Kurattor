import firebase_admin
from firebase_admin import credentials, db
import datetime
import os

def check():
    print("--- ДИАГНОСТИКА FIREBASE ---")
    print(f"Текущее системное время: {datetime.datetime.now()}")
    
    cert_path = "kuraton-firebase-adminsdk-fbsvc-a66f775d22.json"
    if not os.path.exists(cert_path):
        print(f"ОШИБКА: Файл {cert_path} не найден!")
        return

    try:
        cred = credentials.Certificate(cert_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://kuraton-default-rtdb.firebaseio.com'
        })
        print("Инициализация: OK")
        
        # Проверка чтения
        ref = db.reference('/')
        data = ref.get(shallow=True)
        print("Чтение данных: OK")
        print(f"Ключи в базе: {list(data.keys()) if data else 'Пусто'}")
        
    except Exception as e:
        print(f"\nКРИТИЧЕСКАЯ ОШИБКА: {e}")
        if "Invalid JWT Signature" in str(e):
            print("\nПОДСКАЗКА: Ошибка подписи JWT.")
            print("1. ПРОВЕРЬТЕ ЧАСЫ: Ваше время должно быть максимально точным (секунда в секунду).")
            print("2. КЛЮЧ: Возможно, приватный ключ в JSON-файле поврежден или скопирован не полностью.")
        elif "invalid_grant" in str(e):
            print("\nПОДСКАЗКА: Ошибка авторизации. Проверьте, не отозван ли этот сервисный аккаунт в консоли Google Cloud.")

if __name__ == "__main__":
    check()
