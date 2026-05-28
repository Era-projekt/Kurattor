import firebase_admin
from firebase_admin import credentials, auth, db
import random
import json
import datetime
from firebase_config import init_firebase

# ── Initialization ───────────────────────────────────────────────────────────
init_firebase()

# ── Data Lists ───────────────────────────────────────────────────────────────
FIRST_NAMES = [
    "Алибек", "Дамир", "Нурлан", "Алан", "Санжар", "Арман", "Азамат", "Бауыржан", "Ерасыл", "Димаш",
    "Дана", "Алия", "Айгерим", "Гаухар", "Жасмин", "Диана", "Мадина", "Айша", "Камилла", "Сабина"
]
LAST_NAMES = [
    "Сапаров", "Ибрагимов", "Касымов", "Аманжолов", "Оспанов", "Нурланов", "Смагулов", "Абишев", "Муратов", "Болатов",
    "Ахметова", "Султанова", "Муканова", "Есенгалиева", "Турсынова", "Смаилова", "Исаева", "Бекова", "Оразбаева", "Алиева"
]

def generate_random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def seed():
    print("=== ЗАПУСК МАССОВОЙ РЕГИСТРАЦИИ УНИВЕРСИТЕТА ===")
    
    try:
        curators = db.reference('curators').get()
        if not curators:
            print("[ERROR] Кураторы не найдены в базе. Сначала создайте хотя бы одного куратора.")
            return

        total_students_created = 0
        total_curators_updated = 0

        for cid, info in curators.items():
            name = info.get('name', 'Unknown')
            profession = info.get('profession', 'IT')
            print(f"\n[CURATOR] {name} ({profession}) ID: {cid}")
            
            # 15-20 students
            num_students = random.randint(15, 20)
            print(f"-> Начинаю регистрацию {num_students} студентов...")
            
            students_for_curator = info.get('students', {})
            if isinstance(students_for_curator, list): 
                students_for_curator = {str(i): True for i, v in enumerate(students_for_curator) if v}

            for i in range(num_students):
                s_name = generate_random_name()
                s_email = f"student.{cid[-5:]}.{total_students_created}@kuraton.kz"
                password = "Kuraton2026!"
                
                try:
                    # 1. Create in Firebase Auth
                    user = auth.create_user(
                        email=s_email,
                        password=password,
                        display_name=s_name
                    )
                    s_uid = user.uid
                    
                    # 2. Record in users/
                    db.reference(f"users/{s_uid}").set({
                        "name": s_name,
                        "email": s_email,
                        "role": "student",
                        "profession": profession
                    })
                    
                    # 3. Record in students/ with stats
                    attendance = {}
                    # Last 10 days
                    for d in range(10):
                        date_str = (datetime.date.today() - datetime.timedelta(days=d)).isoformat()
                        attendance[date_str] = random.choice([True, True, True, False]) # 75% attendance
                    
                    pct = random.randint(65, 100)
                    letter = "A" if pct >= 90 else "B" if pct >= 75 else "C" if pct >= 60 else "D"
                    gpa = round(pct / 25, 2)

                    db.reference(f"students/{s_uid}").set({
                        "name": s_name,
                        "email": s_email,
                        "profession": profession,
                        "curator_id": cid,
                        "attendance": attendance,
                        "grade": {"pct": pct, "letter": letter, "gpa": gpa}
                    })
                    
                    # 4. Link to curator
                    db.reference(f"curators/{cid}/students/{s_uid}").set(True)
                    
                    total_students_created += 1
                except Exception as e:
                    print(f"   [SKIP] Ошибка для {s_email}: {e}")
                    
            # Update student count
            updated_info = db.reference(f"curators/{cid}").get()
            s_list = updated_info.get('students', {})
            count = len(s_list) if isinstance(s_list, dict) else 0
            db.reference(f"curators/{cid}").update({"student_count": count})
            total_curators_updated += 1

        print("\n" + "="*50)
        print(f"ИТОГ: Успешно обновлено кураторов: {total_curators_updated}")
        print(f"ИТОГ: Всего создано новых студентов: {total_students_created}")
        print(f"Пароль для всех студентов: Kuraton2026!")
        print("="*50)

    except Exception as e:
        print(f"[FATAL ERROR] {e}")

if __name__ == "__main__":
    seed()
