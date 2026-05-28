from firebase_config import init_firebase
from firebase_admin import db

def check():
    init_firebase()
    print("--- DIAGNOSTICS ---")
    curators = db.reference('curators').get()
    
    if not curators:
        print("[!] Критическая ошибка: Узел 'curators' в базе данных ПУСТ.")
        print("Пожалуйста, запустите 'python seed_university.py', чтобы заполнить базу.")
    else:
        print(f"[OK] В базе найдено {len(curators)} кураторов.")
        for cid, data in curators.items():
            print(f" -> {data.get('name')} | Профессия: {data.get('profession')} | Студентов: {data.get('student_count')}")

if __name__ == "__main__":
    check()
