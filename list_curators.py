from firebase_config import init_firebase
from firebase_admin import db

def list_all_curators():
    init_firebase()
    print("\n" + "="*50)
    print(" СПИСОК КУРАТОРОВ ПО СПЕЦИАЛЬНОСТЯМ ")
    print("="*50)
    
    curators = db.reference('curators').get()
    if not curators:
        print("База кураторов пуста.")
        return

    # Группируем по специальностям
    by_spec = {}
    for cid, c in curators.items():
        spec = c.get('profession', 'Без специальности')
        if spec not in by_spec:
            by_spec[spec] = []
        by_spec[spec].append(c)

    for spec, list_c in by_spec.items():
        print(f"\n🔹 {spec.upper()}:")
        for c in list_c:
            count = c.get('student_count', 0)
            status = "✅ ЕСТЬ МЕСТА" if count < 20 else "❌ МЕСТ НЕТ"
            print(f"  - {c.get('name')} | Студентов: {count}/20 | {status}")

    print("\n" + "="*50)

if __name__ == "__main__":
    list_all_curators()
