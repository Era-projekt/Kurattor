"""
seed_data.py - Заполнение Firebase тестовыми данными (Казахские имена)
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import firebase_admin
from firebase_admin import credentials, db, auth
import random
import string

# ── Инициализация Firebase ──────────────────────────────────────────────────
cred = credentials.Certificate("kuraton-firebase-adminsdk-fbsvc-a66f775d22.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://kuraton-default-rtdb.firebaseio.com'
})

# ── Данные специальностей ───────────────────────────────────────────────────
PROFESSIONS = ["IT", "Economics", "Medicine", "Law", "Design"]

PROFESSION_LABELS = {
    "IT":        {"ru": "IT (Информационные технологии)", "kk": "IT (Ақпараттық технологиялар)"},
    "Economics": {"ru": "Экономика",                      "kk": "Экономика"},
    "Medicine":  {"ru": "Медицина",                       "kk": "Медицина"},
    "Law":       {"ru": "Юриспруденция",                  "kk": "Құқықтану"},
    "Design":    {"ru": "Дизайн",                         "kk": "Дизайн"},
}

# ── Кураторы (2 на специальность) ──────────────────────────────────────────
CURATORS_DATA = {
    "IT": [
        {"name": "Ержанов Олжас Бекович",      "email": "olzhas.erzhanov@kuraton.kz"},
        {"name": "Сейткали Арман Мейрамович",  "email": "arman.seitkali@kuraton.kz"},
    ],
    "Economics": [
        {"name": "Мусина Гүлнар Асқарқызы",   "email": "gulnar.musina@kuraton.kz"},
        {"name": "Байжанов Серік Нурланович",  "email": "serik.bayzhanov@kuraton.kz"},
    ],
    "Medicine": [
        {"name": "Алиева Зарина Маратқызы",    "email": "zarina.alieva@kuraton.kz"},
        {"name": "Нурланов Бейбут Ерланович",  "email": "beibut.nurlanov@kuraton.kz"},
    ],
    "Law": [
        {"name": "Токаева Камила Əлібекқызы",  "email": "kamila.tokaeva@kuraton.kz"},
        {"name": "Жуманов Диас Сапарович",     "email": "dias.zhumanov@kuraton.kz"},
    ],
    "Design": [
        {"name": "Садықова Айна Болатқызы",    "email": "aina.sadykova@kuraton.kz"},
        {"name": "Бекова Малика Əлiбекқызы",   "email": "malika.bekova@kuraton.kz"},
    ],
}

# ── Студенческие имена (казахские) ──────────────────────────────────────────
MALE_FIRST = [
    "Алибек", "Нұрлан", "Бауыржан", "Ерлан", "Дəулет", "Арман", "Айбар",
    "Темiрлан", "Алмас", "Жандос", "Айдос", "Медет", "Болат", "Бекзат",
    "Асылбек", "Думан", "Қанат", "Нұрберген", "Ерназар", "Сұлтан",
    "Абылай", "Дəурен", "Мадияр", "Самат", "Руслан", "Ақжол", "Тимур",
    "Азамат", "Санжар", "Ринат",
]
FEMALE_FIRST = [
    "Айгерiм", "Дана", "Жансая", "Мерей", "Гүлнар", "Айнур", "Зарина",
    "Ботакөз", "Дiлназ", "Камила", "Алия", "Меруерт", "Сабина", "Назерке",
    "Ақмарал", "Томирис", "Жулдыз", "Перизат", "Мадина", "Аружан",
    "Диана", "Лəйла", "Сəуле", "Ұлбосын", "Айдана",
]
LAST_NAMES = [
    "Ахметов", "Сейткали", "Мусин", "Байжанов", "Нурланов", "Алиев",
    "Токаев", "Жуманов", "Садықов", "Беков", "Қасымов", "Ержанов",
    "Дүйсенов", "Кенжебаев", "Мамытов", "Оспанов", "Базаров", "Тоқтаров",
    "Рахимов", "Əбенов", "Ислам", "Қожахметов", "Тілеулов", "Серікбаев",
    "Дарменов", "Бейсенов", "Жақсыбеков", "Нұрмағамбетов", "Ниязов",
    "Əлiбеков", "Əмiреев", "Молдабеков",
]

EMAIL_DOMAINS = ["gmail.com", "mail.ru", "yandex.ru", "inbox.ru", "bk.ru", "list.ru"]

def random_email(first: str, last: str) -> str:
    """Генерирует реалистичный email на основе имени (транслит)."""
    TRANSLIT = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ж':'zh','з':'z',
        'и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p',
        'р':'r','с':'s','т':'t','у':'u','ф':'f','х':'kh','ц':'ts','ч':'ch',
        'ш':'sh','щ':'shch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',
        'ə':'ae','ғ':'gh','қ':'q','ң':'ng','ү':'u','ұ':'u','ö':'o','i':'i',
        'ä':'a','ó':'o','á':'a',
    }
    def translit(s):
        return ''.join(TRANSLIT.get(c.lower(), c) for c in s if c.isalpha() or c == ' ').strip()

    f = translit(first[:4]).lower()
    l = translit(last[:7]).lower()
    n = random.randint(1, 99)
    domain = random.choice(EMAIL_DOMAINS)
    return f"{f}.{l}{n}@{domain}"


def generate_attendance(weeks: int = 15) -> dict:
    """Генерирует данные о посещаемости за семестр (15 недель, 2 занятия/нед)."""
    import datetime
    attendance = {}
    today = datetime.date.today()
    for i in range(weeks * 2):
        day_offset = (weeks * 2 - i) * 3  # ~3 дня между занятиями
        date_str = (today - datetime.timedelta(days=day_offset)).strftime("%Y-%m-%d")
        # 70-100% вероятность присутствия
        attendance[date_str] = random.random() > 0.15
    return attendance


def calc_grade(attendance: dict) -> dict:
    """Рассчитывает итоговую оценку на основе посещаемости."""
    total = len(attendance)
    if total == 0:
        return {"pct": 0, "letter": "F", "gpa": 0.0}
    present = sum(1 for v in attendance.values() if v)
    pct = round((present / total) * 100)
    # Добавляем небольшой случайный бонус/штраф ±10%
    pct = max(0, min(100, pct + random.randint(-10, 10)))
    if pct >= 90:   letter, gpa = "A",  4.0
    elif pct >= 80: letter, gpa = "B",  3.0
    elif pct >= 70: letter, gpa = "C",  2.0
    elif pct >= 60: letter, gpa = "D",  1.0
    else:           letter, gpa = "F",  0.0
    return {"pct": pct, "letter": letter, "gpa": gpa}


DEFAULT_PASSWORD = "Kuraton2026!"


def create_user_safe(email: str, name: str = "") -> str | None:
    """Создаёт пользователя Firebase Auth. Возвращает UID или None при ошибке."""
    try:
        user = auth.create_user(email=email, password=DEFAULT_PASSWORD, display_name=name)
        return user.uid
    except Exception as e:
        if "EMAIL_EXISTS" in str(e) or "email-already-exists" in str(e).lower():
            try:
                user = auth.get_user_by_email(email)
                print(f"  [existing] {email} → {user.uid}")
                return user.uid
            except Exception:
                pass
        print(f"  [ERROR] {email}: {e}")
        return None


# ── MAIN SEED LOGIC ─────────────────────────────────────────────────────────
def seed():
    print("=" * 60)
    print("KURATON — Заполнение базы данных тестовыми данными")
    print("=" * 60)

    used_emails = set()

    for profession in PROFESSIONS:
        print(f"\n=== Специальность: {profession} ===")
        curators = CURATORS_DATA[profession]

        for curator_info in curators:
            c_email = curator_info["email"]
            c_name  = curator_info["name"]

            print(f"\n  [CURATOR] {c_name} ({c_email})")
            c_uid = create_user_safe(c_email, c_name)
            if not c_uid:
                print(f"  [SKIP] Куратор {c_email} пропущен.")
                continue

            num_students = random.randint(16, 20)
            student_ids = {}

            for s_idx in range(num_students):
                # Генерация уникального имени и email
                gender = random.choice(["male", "female"])
                if gender == "male":
                    first = random.choice(MALE_FIRST)
                    last  = random.choice(LAST_NAMES)
                    full  = f"{last} {first} Бекович"
                else:
                    first = random.choice(FEMALE_FIRST)
                    last  = random.choice(LAST_NAMES)
                    full  = f"{last} {first} Болатқызы"

                # Уникальный email
                for _ in range(10):
                    email = random_email(first, last)
                    if email not in used_emails:
                        used_emails.add(email)
                        break

                s_uid = create_user_safe(email, full)
                if not s_uid:
                    continue

                # Посещаемость и оценки
                attendance = generate_attendance(15)
                grade      = calc_grade(attendance)

                # Студент в /users/
                db.reference(f"users/{s_uid}").set({
                    "name":       full,
                    "email":      email,
                    "role":       "student",
                    "profession": profession,
                })
                # Студент в /students/
                db.reference(f"students/{s_uid}").set({
                    "name":       full,
                    "email":      email,
                    "profession": profession,
                    "curator_id": c_uid,
                    "attendance": attendance,
                    "grade":      grade,
                    "semester":   1,
                })

                student_ids[s_uid] = True
                print(f"    + [{s_idx+1:02d}/{num_students}] {full} ({email}) -- {grade['letter']} ({grade['pct']}%)")

            # Куратор в /users/
            db.reference(f"users/{c_uid}").set({
                "name":       c_name,
                "email":      c_email,
                "role":       "curator",
                "profession": profession,
            })
            # Куратор в /curators/
            db.reference(f"curators/{c_uid}").set({
                "name":          c_name,
                "email":         c_email,
                "profession":    profession,
                "student_count": len(student_ids),
                "students":      student_ids,
            })
            print(f"  [OK] Куратор {c_name}: {len(student_ids)} студентов зарегистрировано")

    print("\n" + "=" * 60)
    print("[DONE] Заполнение базы данных завершено!")
    print(f"   Пароль для всех аккаунтов: {DEFAULT_PASSWORD}")
    print("=" * 60)


if __name__ == "__main__":
    seed()
