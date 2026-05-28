from firebase_config import init_firebase
from firebase_admin import db
import secrets

def attach_parent():
    init_firebase()
    print("=== ПРИВЯЗКА РОДИТЕЛЬСКОГО ДОСТУПА ===")
    
    # Находим любого студента 1-го курса (или просто первого из списка)
    students_ref = db.reference('students')
    all_students = students_ref.get()
    
    if not all_students:
        print("[ERROR] Студенты не найдены!")
        return

    # Берем первого студента для демонстрации
    sid = list(all_students.keys())[0]
    sname = all_students[sid].get('name', 'Unknown')
    
    # Генерируем уникальный токен
    token = secrets.token_urlsafe(16)
    
    # Сохраняем токен в профиле студента и в глобальной связке
    db.reference(f'students/{sid}/parent_token').set(token)
    db.reference(f'parent_links/{token}').set(sid)
    
    print(f"-> Студент: {sname} (ID: {sid})")
    print(f"-> СУПЕР-ССЫЛКА ДЛЯ РОДИТЕЛЕЙ:")
    print(f"   http://localhost:5000/parent/access/{token}")
    print("\n[DONE] Токен успешно создан и привязан!")

if __name__ == "__main__":
    attach_parent()
