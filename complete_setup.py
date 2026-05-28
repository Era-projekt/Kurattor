import firebase_admin
from firebase_admin import auth, db
import random
import datetime
from firebase_config import init_firebase

# Инициализация
init_firebase()

PROFESSIONS = ["IT", "Economics", "Medicine", "Law", "Design"]
FIRST_NAMES = ["Алибек", "Дамир", "Нурлан", "Алан", "Санжар", "Дана", "Алия", "Айгерим", "Гаухар", "Мадина"]
LAST_NAMES = ["Сапаров", "Ибрагимов", "Касымов", "Аманжолов", "Оспанов", "Ахметова", "Султанова", "Исаева"]

def generate_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def setup_all():
    print("=== ПОЛНАЯ НАСТРОЙКА УНИВЕРСИТЕТА (КУРАТОРЫ + СТУДЕНТЫ + РАСПИСАНИЕ) ===")
    
    # 1. Создаем расписание для каждой специальности
    print("\n[1/3] Настройка расписаний...")
    subjects_pool = ["Высшая математика", "История Казахстана", "Английский язык", "Профильный предмет", "Физкультура", "Психология"]
    for prof in PROFESSIONS:
        days = ["mon", "tue", "wed", "thu", "fri", "sat"]
        times = ["09-00", "10-30", "12-00", "13-30"]
        total_sched = {}
        for day in days:
            day_sched = {}
            for t in times:
                day_sched[t] = {
                    "subject": random.choice(subjects_pool),
                    "room": f"A-{random.randint(100, 500)}",
                    "time": t.replace("-", ":")
                }
            total_sched[day] = day_sched
        db.reference(f"specialty_schedules/{prof}").set(total_sched)

    # 2. Создаем кураторов и студентов
    print("\n[2/3] Создание кураторов и студентов...")
    for prof in PROFESSIONS:
        c_name = generate_name()
        c_email = f"curator.{prof.lower()}@kuraton.kz"
        password = "Kuraton2026!"
        
        try:
            # Создаем Gmail/Email пользователя в Firebase Auth
            try:
                user = auth.get_user_by_email(c_email)
                c_uid = user.uid
                print(f" Куратор {c_email} уже существует.")
            except:
                user = auth.create_user(email=c_email, password=password, display_name=c_name)
                c_uid = user.uid
                print(f" Создан куратор: {c_name} ({prof})")

            # Данные куратора
            db.reference(f"users/{c_uid}").set({"name": c_name, "email": c_email, "role": "curator", "profession": prof})
            db.reference(f"curators/{c_uid}").set({"name": c_name, "email": c_email, "profession": prof, "student_count": 0})

            # Регистрируем 15 студентов для этого куратора
            num_students = 15
            for i in range(num_students):
                s_name = generate_name()
                s_email = f"student.{prof.lower()}.{i}@kuraton.kz"
                
                try:
                    try:
                        s_user = auth.get_user_by_email(s_email)
                        s_uid = s_user.uid
                    except:
                        s_user = auth.create_user(email=s_email, password=password, display_name=s_name)
                        s_uid = s_user.uid
                    
                    # Данные студента
                    db.reference(f"users/{s_uid}").set({"name": s_name, "email": s_email, "role": "student", "profession": prof})
                    
                    pct = random.randint(70, 98)
                    letter = "A" if pct >= 90 else "B" if pct >= 75 else "C"
                    db.reference(f"students/{s_uid}").set({
                        "name": s_name, "email": s_email, "profession": prof, 
                        "curator_id": c_uid, "attendance": {}, "grade": {"pct": pct, "letter": letter}
                    })
                    
                    # Привязка
                    db.reference(f"curators/{c_uid}/students/{s_uid}").set(True)
                except Exception as e:
                    pass # Пропускаем если студент уже есть

            # Обновляем счетчик
            db.reference(f"curators/{c_uid}").update({"student_count": num_students})
            
        except Exception as e:
            print(f"Ошибка при создании {prof}: {e}")

    print("\n[3/3] Готово! Теперь база наполнена.")
    print("Все пароли: Kuraton2026!")

if __name__ == "__main__":
    setup_all()
