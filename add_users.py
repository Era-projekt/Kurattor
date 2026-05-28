"""
add_users.py — Добавление конкретных аккаунтов и дополнительных студентов Design
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import random
import datetime
import firebase_admin
from firebase_admin import credentials, db, auth

# ── Firebase ──────────────────────────────────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate("kuraton-firebase-adminsdk-fbsvc-a66f775d22.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://kuraton-default-rtdb.firebaseio.com'
    })

DEFAULT_PASSWORD = "Kuraton2026!"

# ── Казахские имена ───────────────────────────────────────────────────────────
MALE_FIRST = [
    "Алибек","Нұрлан","Бауыржан","Ерлан","Дəулет","Арман","Айбар",
    "Темiрлан","Алмас","Жандос","Айдос","Медет","Болат","Бекзат",
    "Асылбек","Думан","Қанат","Нұрберген","Ерназар","Сұлтан",
    "Абылай","Дəурен","Мадияр","Самат","Руслан","Ақжол","Тимур",
]
FEMALE_FIRST = [
    "Айгерiм","Дана","Жансая","Мерей","Гүлнар","Айнур","Зарина",
    "Ботакөз","Дiлназ","Камила","Алия","Меруерт","Сабина","Назерке",
    "Ақмарал","Томирис","Жулдыз","Перизат","Мадина","Аружан",
    "Диана","Лəйла","Сəуле","Айдана",
]
LAST_NAMES = [
    "Ахметов","Сейткали","Мусин","Байжанов","Нурланов","Алиев",
    "Токаев","Жуманов","Садықов","Беков","Қасымов","Ержанов",
    "Дүйсенов","Кенжебаев","Мамытов","Оспанов","Базаров","Тоқтаров",
    "Рахимов","Əбенов","Ислам","Қожахметов","Тілеулов","Серікбаев",
]
EMAIL_DOMAINS = ["gmail.com","mail.ru","yandex.ru","inbox.ru","bk.ru"]

TRANSLIT = {
    'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ж':'zh','з':'z',
    'и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p',
    'р':'r','с':'s','т':'t','у':'u','ф':'f','х':'kh','ц':'ts','ч':'ch',
    'ш':'sh','щ':'shch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',
    'ə':'ae','ғ':'gh','қ':'q','ң':'ng','ү':'u','ұ':'u','i':'i',
}

def translit(s):
    return ''.join(TRANSLIT.get(c.lower(), c) for c in s if c.isalpha()).strip()

def gen_email(first, last):
    f = translit(first[:4]).lower()
    l = translit(last[:6]).lower()
    return f"{f}.{l}{random.randint(1,99)}@{random.choice(EMAIL_DOMAINS)}"

def gen_attendance(weeks=15):
    att = {}
    today = datetime.date.today()
    for i in range(weeks * 2):
        d = today - datetime.timedelta(days=(weeks*2 - i)*3)
        att[d.strftime("%Y-%m-%d")] = random.random() > 0.15
    return att

def calc_grade(att):
    total = len(att)
    if not total:
        return {"pct": 0, "letter": "F", "gpa": 0.0}
    present = sum(1 for v in att.values() if v)
    pct = max(0, min(100, round((present/total)*100) + random.randint(-8, 8)))
    if pct >= 90: letter, gpa = "A", 4.0
    elif pct >= 80: letter, gpa = "B", 3.0
    elif pct >= 70: letter, gpa = "C", 2.0
    elif pct >= 60: letter, gpa = "D", 1.0
    else:           letter, gpa = "F", 0.0
    return {"pct": pct, "letter": letter, "gpa": gpa}

def create_user(email, name, password=DEFAULT_PASSWORD):
    try:
        u = auth.create_user(email=email, password=password, display_name=name)
        print(f"  [NEW]  {name} ({email})")
        return u.uid
    except Exception as e:
        if "email-already-exists" in str(e).lower() or "EMAIL_EXISTS" in str(e):
            u = auth.get_user_by_email(email)
            print(f"  [EXISTS] {name} ({email}) -> {u.uid}")
            return u.uid
        print(f"  [ERROR] {email}: {e}")
        return None

def save_student(uid, name, email, profession, curator_id=None):
    att   = gen_attendance()
    grade = calc_grade(att)
    db.reference(f"users/{uid}").set({
        "name": name, "email": email,
        "role": "student", "profession": profession
    })
    db.reference(f"students/{uid}").set({
        "name": name, "email": email,
        "profession": profession,
        "curator_id": curator_id,
        "attendance": att,
        "grade": grade,
        "semester": 1,
    })
    return grade

def find_design_curator():
    """Возвращает uid куратора Design с наименьшим числом студентов, или None."""
    curators = db.reference("curators").get() or {}
    best_uid, best_cnt = None, 999
    for uid, data in curators.items():
        if data.get("profession") == "Design" and data.get("student_count", 0) < 20:
            if data.get("student_count", 0) < best_cnt:
                best_uid, best_cnt = uid, data.get("student_count", 0)
    return best_uid

def attach_to_curator(curator_uid, student_uid):
    """Привязывает студента к куратору в /curators/{uid}/students/ и обновляет счётчик."""
    ref = db.reference(f"curators/{curator_uid}")
    data = ref.get() or {}
    cnt = data.get("student_count", 0)
    ref.update({"student_count": cnt + 1})
    db.reference(f"curators/{curator_uid}/students/{student_uid}").set(True)
    db.reference(f"students/{student_uid}").update({"curator_id": curator_uid})

# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("KURATON — Добавление специальных аккаунтов и студентов Design")
print("=" * 60)

# ── 1. Два конкретных аккаунта ──────────────────────────────────────────────
SPECIFIC_ACCOUNTS = [
    {"email": "alakankalan@gmail.com",  "name": "Аланкалан Айгүл Бекқызы"},
    {"email": "zhom05025@gmail.com",    "name": "Жомарт Нұрлан Серікұлы"},
]

print("\n[1] Добавление конкретных аккаунтов...")
cur_uid = find_design_curator()
print(f"    Куратор Design: {cur_uid or 'НЕ НАЙДЕН — назначение пропущено'}")

for acc in SPECIFIC_ACCOUNTS:
    uid = create_user(acc["email"], acc["name"])
    if uid:
        grade = save_student(uid, acc["name"], acc["email"], "Design", cur_uid)
        if cur_uid:
            attach_to_curator(cur_uid, uid)
        print(f"    -> Оценка: {grade['letter']} ({grade['pct']}%)")

# ── 2. Дополнительные ~18 студентов Design ──────────────────────────────────
print(f"\n[2] Добавление 18 дополнительных студентов Design...")
extra_cur_uid = find_design_curator()  # получаем актуального куратора

used_emails = set()
added = 0
while added < 18:
    gender = random.choice(["m", "f"])
    if gender == "m":
        first = random.choice(MALE_FIRST)
        last  = random.choice(LAST_NAMES)
        full  = f"{last} {first} Болатұлы"
    else:
        first = random.choice(FEMALE_FIRST)
        last  = random.choice(LAST_NAMES)
        full  = f"{last} {first} Бекқызы"

    email = gen_email(first, last)
    if email in used_emails:
        continue
    used_emails.add(email)

    uid = create_user(email, full)
    if uid:
        grade = save_student(uid, full, email, "Design", extra_cur_uid)
        if extra_cur_uid:
            attach_to_curator(extra_cur_uid, uid)
        print(f"    [{added+1:02d}/18] {full} -- {grade['letter']} ({grade['pct']}%)")
        added += 1
        # Обновляем куратора если лимит достигнут
        extra_cur_uid = find_design_curator()

# ── 3. Проверим/добавим кураторов других специальностей ─────────────────────
EXTRA_CURATORS = [
    {"name": "Əбдінов Руслан Маратұлы",   "email": "ruslan.abdinov@kuraton.kz",   "profession": "Economics"},
    {"name": "Қасымова Дәмел Нұрланқызы", "email": "damel.qasymova@kuraton.kz",   "profession": "IT"},
    {"name": "Жақыпов Айдар Серікұлы",    "email": "aidar.zhaqypov@kuraton.kz",   "profession": "Medicine"},
    {"name": "Бейсенова Алима Болатқызы", "email": "alima.beisenova@kuraton.kz",  "profession": "Law"},
    {"name": "Нұрбеков Ержан Дүйсенұлы",  "email": "erzhan.nurbekov@kuraton.kz",  "profession": "Design"},
]

print("\n[3] Добавление дополнительных кураторов...")
for c in EXTRA_CURATORS:
    uid = create_user(c["email"], c["name"])
    if uid:
        db.reference(f"users/{uid}").set({
            "name": c["name"], "email": c["email"],
            "role": "curator", "profession": c["profession"]
        })
        # Создаём запись куратора только если не существует
        existing = db.reference(f"curators/{uid}").get()
        if not existing:
            db.reference(f"curators/{uid}").set({
                "name": c["name"], "email": c["email"],
                "profession": c["profession"], "student_count": 0
            })
            print(f"    -> Куратор создан: {c['name']} ({c['profession']})")
        else:
            print(f"    -> Куратор уже существует: {c['name']}")

print("\n" + "=" * 60)
print("[DONE] Готово!")
print(f"  Пароль: {DEFAULT_PASSWORD}")
print("  Конкретные аккаунты:")
for a in SPECIFIC_ACCOUNTS:
    print(f"    {a['email']} / {DEFAULT_PASSWORD}  -- Design")
print("=" * 60)
