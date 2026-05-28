import firebase_admin
from firebase_admin import credentials, db, auth
import datetime

# ── Firebase Initialization ──────────────────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate("kuraton-firebase-adminsdk-fbsvc-a66f775d22.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://kuraton-default-rtdb.firebaseio.com'
    })

def get_uid_by_email(email):
    try:
        user = auth.get_user_by_email(email)
        return user.uid
    except:
        return None

# ── 1. Educational Materials (All Specialties) ───────────────────────────────
print("[1] Добавление материалов для всех специальностей...")
materials = [
    {"name": "Python: От новичка до профи", "type": "pdf", "profession": "IT"},
    {"name": "Введение в облачные вычисления", "type": "vid", "profession": "IT"},
    {"name": "Эконометрика в примерах", "type": "pdf", "profession": "Economics"},
    {"name": "Мировая экономика 2024", "type": "ppt", "profession": "Economics"},
    {"name": "Клиническая фармакология", "type": "pdf", "profession": "Medicine"},
    {"name": "Хирургическая практика (Видео)", "type": "vid", "profession": "Medicine"},
    {"name": "Конституционное право РК", "type": "pdf", "profession": "Law"},
    {"name": "Криминалистика: Сборник", "type": "doc", "profession": "Law"},
    {"name": "Теория цвета в дизайне", "type": "ppt", "profession": "Design"},
    {"name": "Моделирование в Blender 3D", "type": "vid", "profession": "Design"},
]

files_ref = db.reference("files")
files_ref.delete()
for m in materials:
    m["date"] = datetime.date.today().strftime("%d.%m.%Y")
    m["url"] = "#"
    files_ref.push(m)

# ── 2. Unique Schedules for 5 Curators ────────────────────────────────────────
print("\n[2] Создание уникальных расписаний для 5 специальностей...")

CURATORS = {
    "IT (Дамель)":        "damel.qasymova@kuraton.kz",
    "ECON (Руслан)":     "ruslan.abdinov@kuraton.kz",
    "MED (Айдар)":       "aidar.zhaqypov@kuraton.kz",
    "LAW (Алима)":       "alima.beisenova@kuraton.kz",
    "DESIGN (Ержан)":    "erzhan.nurbekov@kuraton.kz"
}

SCHEDULES = {
    "IT (Дамель)": {
        "mon": {"09:00": {"subject": "Алгоритмы"}, "11:00": {"subject": "Python"}},
        "tue": {"10:00": {"subject": "Сети"}},
        "wed": {"09:00": {"subject": "ОС"}, "14:00": {"subject": "Базы данных"}}
    },
    "ECON (Руслан)": {
        "mon": {"10:00": {"subject": "Микроэкономика"}},
        "wed": {"09:00": {"subject": "Бухучет"}, "11:00": {"subject": "Маркетинг"}},
        "fri": {"12:00": {"subject": "Финансы"}}
    },
    "MED (Айдар)": {
        "tue": {"09:00": {"subject": "Анатомия"}, "13:00": {"subject": "Хирургия"}},
        "thu": {"11:00": {"subject": "Биохимия"}},
        "sat": {"10:00": {"subject": "Практика"}}
    },
    "LAW (Алима)": {
        "mon": {"11:00": {"subject": "Гражданское право"}},
        "wed": {"10:00": {"subject": "Уголовное право"}},
        "thu": {"14:00": {"subject": "Римское право"}}
    },
    "DESIGN (Ержан)": {
        "tue": {"11:00": {"subject": "Композиция"}, "14:00": {"subject": "Sketching"}},
        "fri": {"10:00": {"subject": "UI/UX Дизайн"}},
        "sat": {"12:00": {"subject": " Blender 3D"}}
    }
}

for label, email in CURATORS.items():
    uid = get_uid_by_email(email)
    if uid:
        db.reference(f"schedules/{uid}").set(SCHEDULES[label])
        print(f"    ✓ Расписание обновлено: {label}")
    else:
        print(f"    ✗ Ошибка: Куратор {email} не найден")

print("\n[SUCCESS] Все материалы и расписания загружены!")
