import firebase_admin
from firebase_admin import credentials, auth, db
import json

def rebuild():
    print("--- ПЕРЕСОЗДАНИЕ АККАУНТА КУРАТОРА ---")
    try:
        # 1. Инициализация (с нашим фиксом JWT)
        with open("kuraton-firebase-adminsdk-fbsvc-0ce5270aaf.json", "r") as f:
            si = json.load(f)
        pk = si.get("private_key", "")
        si["private_key"] = pk.replace("\\n", "\n")
        
        cred = credentials.Certificate(si)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://kuraton-default-rtdb.firebaseio.com'
            })
        
        email = "beibut.nurlanov@kuraton.kz"
        password = "Kuraton2026!"
        
        # 2. Удаляем старый аккаунт, если он "битый"
        try:
            old_user = auth.get_user_by_email(email)
            auth.delete_user(old_user.uid)
            print(f"[CLEAN] Старый аккаунт {email} удален для чистого пересоздания.")
        except:
            print(f"[INFO] Аккаунт {email} еще не существовал.")
            
        # 3. Создаем новый чистый аккаунт
        new_user = auth.create_user(
            email=email,
            password=password,
            display_name="Нурланов Бейбут"
        )
        print(f"[SUCCESS] Аккаунт СОЗДАН! UID: {new_user.uid}")
        
        # 4. Привязываем роль в базе данных
        db.reference(f"users/{new_user.uid}").set({
            "name": "Нурланов Бейбут",
            "email": email,
            "role": "curator",
            "profession": "IT"
        })
        print(f"[SUCCESS] Роль куратора прописана в базе.")
        
        print("\n=== ТЕПЕРЬ ПОПРОБУЙТЕ ВОЙТИ ===")
        print(f"Email: {email}")
        print(f"Password: {password}")
        
    except Exception as e:
        print(f"\n[ERROR] Что-то пошло не так: {e}")
        if "Invalid JWT Signature" in str(e):
             print("\nКРИТИЧЕСКИ: Ошибка JWT все еще мешает бэкенду. Проверьте время на компьютере!")

if __name__ == "__main__":
    rebuild()
