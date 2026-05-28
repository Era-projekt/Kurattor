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

SCHED_TEMPLATES = {
    "IT": {
        "mon": {
            "09-00": {"subject": "Высшая математика", "type": "Лекция", "teacher": "проф. Сапаров А. Б.", "room": "A-305", "time": "09:00"},
            "10-30": {"subject": "Высшая математика", "type": "Практика", "teacher": "доц. Султанова Д. К.", "room": "A-310", "time": "10:30"}
        },
        "tue": {
            "09-00": {"subject": "Алгоритмы и структуры данных", "type": "Лекция", "teacher": "доц. Ибрагимов М. С.", "room": "A-204", "time": "09:00"},
            "10-30": {"subject": "Алгоритмы и структуры данных", "type": "Практика", "teacher": "ассист. Оспанов Д. А.", "room": "A-208", "time": "10:30"}
        },
        "wed": {
            "09-00": {"subject": "История Казахстана", "type": "Лекция", "teacher": "проф. Ахметова М. Б.", "room": "A-105", "time": "09:00"},
            "10-30": {"subject": "Высшая математика", "type": "Практика", "teacher": "доц. Султанова Д. К.", "room": "A-310", "time": "10:30"}
        },
        "thu": {
            "09-00": {"subject": "Алгоритмы и структуры данных", "type": "Практика", "teacher": "ассист. Оспанов Д. А.", "room": "A-208", "time": "09:00"},
            "10-30": {"subject": "История Казахстана", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "A-108", "time": "10:30"}
        },
        "fri": {
            "09-00": {"subject": "История Казахстана", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "A-108", "time": "09:00"},
            "10-30": {"subject": "Физическая культура", "type": "Практика", "teacher": "тренер Касымов А. С.", "room": "Спортзал", "time": "10:30"}
        }
    },
    "Economics": {
        "mon": {
            "09-00": {"subject": "Микроэкономика", "type": "Лекция", "teacher": "проф. Касымов А. С.", "room": "A-401", "time": "09:00"},
            "10-30": {"subject": "Микроэкономика", "type": "Практика", "teacher": "доц. Султанова М. Б.", "room": "A-405", "time": "10:30"}
        },
        "tue": {
            "09-00": {"subject": "Эконометрика", "type": "Лекция", "teacher": "проф. Аманжолов Н. А.", "room": "A-210", "time": "09:00"},
            "10-30": {"subject": "Эконометрика", "type": "Практика", "teacher": "ассист. Сапаров А. Б.", "room": "A-212", "time": "10:30"}
        },
        "wed": {
            "09-00": {"subject": "История Казахстана", "type": "Лекция", "teacher": "проф. Ахметова М. Б.", "room": "A-105", "time": "09:00"},
            "10-30": {"subject": "Микроэкономика", "type": "Практика", "teacher": "доц. Султанова М. Б.", "room": "A-405", "time": "10:30"}
        },
        "thu": {
            "09-00": {"subject": "Эконометрика", "type": "Практика", "teacher": "ассист. Сапаров А. Б.", "room": "A-212", "time": "09:00"},
            "10-30": {"subject": "История Казахстана", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "A-108", "time": "10:30"}
        },
        "fri": {
            "09-00": {"subject": "История Казахстана", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "A-108", "time": "09:00"},
            "10-30": {"subject": "Физическая культура", "type": "Практика", "teacher": "тренер Касымов А. С.", "room": "Спортзал", "time": "10:30"}
        }
    },
    "Medicine": {
        "mon": {
            "09-00": {"subject": "Анатомия человека", "type": "Лекция", "teacher": "проф. Ибрагимов М. С.", "room": "A-101", "time": "09:00"},
            "10-30": {"subject": "Анатомия человека", "type": "Практика", "teacher": "доц. Оспанов Д. А.", "room": "A-103", "time": "10:30"}
        },
        "tue": {
            "09-00": {"subject": "Общая биология", "type": "Лекция", "teacher": "проф. Ахметова М. Б.", "room": "A-201", "time": "09:00"},
            "10-30": {"subject": "Общая биология", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "A-204", "time": "10:30"}
        },
        "wed": {
            "09-00": {"subject": "История Казахстана", "type": "Лекция", "teacher": "проф. Ахметова М. Б.", "room": "A-105", "time": "09:00"},
            "10-30": {"subject": "Анатомия человека", "type": "Практика", "teacher": "доц. Оспанов Д. А.", "room": "A-103", "time": "10:30"}
        },
        "thu": {
            "09-00": {"subject": "Общая биология", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "A-204", "time": "09:00"},
            "10-30": {"subject": "История Казахстана", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "A-108", "time": "10:30"}
        },
        "fri": {
            "09-00": {"subject": "История Казахстана", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "A-108", "time": "09:00"},
            "10-30": {"subject": "Физическая культура", "type": "Практика", "teacher": "тренер Касымов А. С.", "room": "Спортзал", "time": "10:30"}
        }
    },
    "Law": {
        "mon": {
            "09-00": {"subject": "Конституционное право", "type": "Лекция", "teacher": "проф. Аманжолов Н. А.", "room": "A-301", "time": "09:00"},
            "10-30": {"subject": "Конституционное право", "type": "Практика", "teacher": "доц. Сапаров А. Б.", "room": "A-304", "time": "10:30"}
        },
        "tue": {
            "09-00": {"subject": "Теория государства и права", "type": "Лекция", "teacher": "проф. Ибрагимов М. С.", "room": "A-110", "time": "09:00"},
            "10-30": {"subject": "Теория государства и права", "type": "Практика", "teacher": "доц. Оспанов Д. А.", "room": "A-114", "time": "10:30"}
        },
        "wed": {
            "09-00": {"subject": "История Казахстана", "type": "Лекция", "teacher": "проф. Ахметова М. Б.", "room": "A-105", "time": "09:00"},
            "10-30": {"subject": "Конституционное право", "type": "Практика", "teacher": "доц. Сапаров А. Б.", "room": "A-304", "time": "10:30"}
        },
        "thu": {
            "09-00": {"subject": "Теория государства и права", "type": "Практика", "teacher": "доц. Оспанов Д. А.", "room": "A-114", "time": "09:00"},
            "10-30": {"subject": "История Казахстана", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "A-108", "time": "10:30"}
        },
        "fri": {
            "09-00": {"subject": "История Казахстана", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "A-108", "time": "09:00"},
            "10-30": {"subject": "Физическая культура", "type": "Практика", "teacher": "тренер Касымов А. С.", "room": "Спортзал", "time": "10:30"}
        }
    },
    "Design": {
        "mon": {
            "09-00": {"subject": "История искусств", "type": "Лекция", "teacher": "проф. Султанова Д. К.", "room": "A-501", "time": "09:00"},
            "10-30": {"subject": "История искусств", "type": "Практика", "teacher": "доц. Ахметова М. Б.", "room": "A-503", "time": "10:30"}
        },
        "tue": {
            "09-00": {"subject": "Рисунок и живопись", "type": "Лекция", "teacher": "проф. Касымов А. С.", "room": "Мастерская-1", "time": "09:00"},
            "10-30": {"subject": "Рисунок и живопись", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "Мастерская-2", "time": "10:30"}
        },
        "wed": {
            "09-00": {"subject": "История Казахстана", "type": "Лекция", "teacher": "проф. Ахметова М. Б.", "room": "A-105", "time": "09:00"},
            "10-30": {"subject": "История искусств", "type": "Практика", "teacher": "доц. Ахметова М. Б.", "room": "A-503", "time": "10:30"}
        },
        "thu": {
            "09-00": {"subject": "Рисунок и живопись", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "Мастерская-2", "time": "09:00"},
            "10-30": {"subject": "История Казахстана", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "A-108", "time": "10:30"}
        },
        "fri": {
            "09-00": {"subject": "История Казахстана", "type": "Практика", "teacher": "доц. Исаева С. Н.", "room": "A-108", "time": "09:00"},
            "10-30": {"subject": "Физическая культура", "type": "Практика", "teacher": "тренер Касымов А. С.", "room": "Спортзал", "time": "10:30"}
        }
    }
}

def generate_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def setup_all():
    print("=== ПОЛНАЯ НАСТРОЙКА УНИВЕРСИТЕТА (КУРАТОРЫ + СТУДЕНТЫ + РАСПИСАНИЕ) ===")
    
    # 1. Создаем расписание для каждой специальности
    print("\n[1/3] Настройка расписаний...")
    db.reference("specialty_schedules").set(SCHED_TEMPLATES)

    # 2. Создаем кураторов и студентов
    print("\n[2/3] Создание кураторов и студентов...")
    for prof in PROFESSIONS:
        c_name = generate_name()
        c_email = f"curator.{prof.lower()}@gmail.com"
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
            db.reference(f"users/{c_uid}").set({"name": c_name, "email": c_email, "role": "curator", "profession": prof, "password": password})
            db.reference(f"curators/{c_uid}").set({"name": c_name, "email": c_email, "profession": prof, "student_count": 0})

            # Регистрируем 15 студентов для этого куратора
            num_students = 15
            for i in range(num_students):
                s_name = generate_name()
                s_email = f"student.{prof.lower()}.{i}@gmail.com"
                
                try:
                    try:
                        s_user = auth.get_user_by_email(s_email)
                        s_uid = s_user.uid
                    except:
                        s_user = auth.create_user(email=s_email, password=password, display_name=s_name)
                        s_uid = s_user.uid
                    
                    # Данные студента
                    db.reference(f"users/{s_uid}").set({"name": s_name, "email": s_email, "role": "student", "profession": prof, "password": password})
                    
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
