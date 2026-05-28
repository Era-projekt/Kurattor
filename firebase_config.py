import firebase_admin
from firebase_admin import credentials, db

def init_firebase():
    """Инициализация Firebase Admin SDK: Финальная попытка исправления с локальным фоллбэком"""
    import json
    try:
        with open("kuraton-firebase-adminsdk-fbsvc-0ce5270aaf.json", "r") as f:
            si = json.load(f)
        
        # Силовое форматирование ключа
        pk = si.get("private_key", "")
        if "\\n" in pk:
            pk = pk.replace("\\n", "\n")
        si["private_key"] = pk

        cred = credentials.Certificate(si)
        
        # Инициализация с явным указанием проекта из JSON
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://kuraton-default-rtdb.firebaseio.com',
            'projectId': si.get('project_id')
        })
        print(f"Firebase Admin SDK успешно инициализирован для проекта: {si.get('project_id')}")
    except Exception as e:
        print(f"ОШИБКА ИНИЦИАЛИЗАЦИИ FIREBASE (Запускаем локальный/офлайн режим): {e}")
        try:
            import mock_firebase
            mock_firebase.patch_firebase_admin()
        except Exception as mock_err:
            print(f"Критическая ошибка при запуске локального режима: {mock_err}")

