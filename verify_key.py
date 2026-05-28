import json
import time
import datetime
from google.auth import jwt
from google.auth import crypt

def diag():
    print("--- 1. ПРОВЕРКА ВРЕМЕНИ ---")
    now = time.time()
    print(f"Unix Time: {now}")
    print(f"Local Time: {datetime.datetime.now()}")
    
    cert_path = "kuraton-firebase-adminsdk-fbsvc-0ce5270aaf.json"
    try:
        with open(cert_path, "r") as f:
            data = json.load(f)
        
        print("\n--- 2. ПРОВЕРКА КЛЮЧА ---")
        print(f"Project ID: {data.get('project_id')}")
        print(f"Client Email: {data.get('client_email')}")
        
        pk = data.get("private_key", "")
        # Очистка ключа
        pk = pk.replace("\\n", "\n")
        
        print(f"Длина ключа: {len(pk)} символов")
        
        # Попытка создать подписанный JWT (тест алгоритма и ключа)
        print("\n--- 3. ТЕСТ ПОДПИСИ (JWT SIGNING) ---")
        signer = crypt.RSASigner.from_service_account_info(data)
        
        payload = {'test': 'data', 'iat': int(now), 'exp': int(now) + 3600}
        signed_jwt = jwt.encode(signer, payload)
        print("Подпись успешно создана! (Алгоритм и ключ технически исправны)")
        
        print("\nИТОГ: Если подпись создана, но Firebase все равно пишет 'Invalid JWT Signature',")
        print("значит проблема либо в РАССИНХРОНИЗАЦИИ ВРЕМЕНИ (сверьтесь с time.is),")
        print("либо этот ключ был ОТОЗВАН в консоли Google Cloud.")

    except Exception as e:
        print(f"\n--- ОШИБКА ДИАГНОСТИКИ ---")
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Описание: {e}")

if __name__ == "__main__":
    diag()
