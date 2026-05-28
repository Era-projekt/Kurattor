import firebase_admin
from firebase_admin import credentials, db, auth
import datetime

from firebase_config import init_firebase

# ── Firebase Initialization ──────────────────────────────────────────────────
init_firebase()

def create_or_get_curator(email, name, profession):
    try:
        user = auth.get_user_by_email(email)
        uid = user.uid
        print(f"[EXISTS] Куратор {name} уже есть.")
    except:
        user = auth.create_user(email=email, password="Kuraton2026!", display_name=name)
        uid = user.uid
        print(f"[NEW] Создан куратор {name}.")

    db.reference(f"users/{uid}").set({
        "name": name, "email": email, "role": "curator", "profession": profession
    })
    db.reference(f"curators/{uid}").update({
        "name": name, "email": email, "profession": profession
    })
    return uid

# ── 1. Setup Nurlanov Beibut ──────────────────────────────────────────────────
email = "beibut.nurlanov@kuraton.kz"
name = "Нурланов Бейбут"
prof = "IT"
cid = create_or_get_curator(email, name, prof)

# ── 2. Add Materials ─────────────────────────────────────────────────────────
print("[2] Добавление материалов...")
materials = [
    {"name": "Лекция: Инновации в IT (Слайды)", "type": "pdf", "profession": "IT"},
    {"name": "Практикум: Python для начинающих", "type": "doc", "profession": "IT"},
    {"name": "Видео: Проектирование БД", "type": "vid", "profession": "IT"},
]
for m in materials:
    m["date"] = datetime.date.today().strftime("%d.%m.%Y")
    m["url"] = "#"
    db.reference("files").push(m)

# ── 3. Setup Schedule (1 Lecture, 2 Practices) ──────────────────────────────
print("[3] Создание расписания...")
schedule = {
    "mon": {"09-00": {"subject": "Инновации в IT (Лекция)", "room": "405", "time": "09:00"}},
    "wed": {"11-00": {"subject": "Разработка на Python (Практика)", "room": "210", "time": "11:00"}},
    "fri": {"14-00": {"subject": "Базы данных (Практика)", "room": "302", "time": "14:00"}}
}
db.reference(f"schedules/{cid}").set(schedule)

# ── 4. Assign Students & Add Attendance ─────────────────────────────────────
print("[4] Назначение студентов и посещаемость...")
# Возьмем несколько студентов без куратора или создадим новых
students_uids = []
for i in range(3):
    s_email = f"student.beibuta{i}@gmail.com"
    try:
        s_user = auth.get_user_by_email(s_email)
        s_uid = s_user.uid
    except:
        s_user = auth.create_user(email=s_email, password="Kuraton2026!", display_name=f"Студент Бейбута {i+1}")
        s_uid = s_user.uid
    
    db.reference(f"users/{s_uid}").set({"name": f"Студент Бейбута {i+1}", "email": s_email, "role": "student", "profession": "IT"})
    
    att = {
        "2026-04-01": True,
        "2026-04-03": True
    }
    db.reference(f"students/{s_uid}").set({
        "name": f"Студент Бейбута {i+1}", "email": s_email, "profession": "IT",
        "curator_id": cid, "attendance": att, "grade": {"pct": 100, "letter": "A", "gpa": 4.0}
    })
    db.reference(f"curators/{cid}/students/{s_uid}").set(True)
    students_uids.append(s_uid)

# Update student count
db.reference(f"curators/{cid}").update({"student_count": len(students_uids)})

print(f"\n[DONE] Все готово! Куратор: {email}, Пароль: Kuraton2026!")
