from firebase_config import init_firebase
from firebase_admin import db

def list_parents():
    init_firebase()
    print("\n" + "="*60)
    print(" СПИСОК ССЫЛОК ДЛЯ РОДИТЕЛЕЙ (ДОСТУП К ОЦЕНКАМ) ")
    print("="*60)
    
    links = db.reference('parent_links').get()
    if not links:
        print("[!] Ссылки еще не созданы.")
        print("Запустите 'python attach_parent.py', чтобы создать первую ссылку.")
        return

    for token, sid in links.items():
        student = db.reference(f'students/{sid}').get()
        if student:
            name = student.get('name', 'Unknown')
            prof = student.get('profession', 'IT')
            print(f"\n👤 Студент: {name} ({prof})")
            print(f"🔗 Ссылка для родителя:")
            print(f"   http://localhost:5000/parent/access/{token}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    list_parents()
