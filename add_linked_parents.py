import firebase_admin
from firebase_admin import auth, db
import datetime
import random
from firebase_config import init_firebase

init_firebase()

password = "Kuraton2026!"

def transliterate(text):
    text = text.lower().strip()
    mapping = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
        'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts',
        'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'y', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'ә': 'a', 'і': 'i', 'ң': 'n', 'ғ': 'g', 'ү': 'u', 'ұ': 'u', 'қ': 'k', 'ө': 'o',
        'һ': 'h'
    }
    res = []
    for char in text:
        res.append(mapping.get(char, char))
    return "".join(res)

def create_or_get_user(email, name, role, profession=None, child_id=None):
    try:
        user = auth.get_user_by_email(email)
        uid = user.uid
        print(f"Пользователь {email} уже существует.")
    except Exception:
        user = auth.create_user(email=email, password=password, display_name=name)
        uid = user.uid
        print(f"Создан новый пользователь: {name} ({email})")
    
    user_data = {
        "name": name,
        "email": email,
        "role": role,
        "password": password
    }
    if profession:
        user_data["profession"] = profession
    if child_id:
        user_data["child_id"] = child_id
        
    db.reference(f"users/{uid}").set(user_data)
    return uid

IT_STUDENTS = [
    {"s_first": "Алибек", "s_last": "Касымов", "p_first": "Оспан"},
    {"s_first": "Алихан", "s_last": "Ахметов", "p_first": "Серик"},
    {"s_first": "Диас", "s_last": "Ибрагимов", "p_first": "Канат"},
    {"s_first": "Санжар", "s_last": "Оспанов", "p_first": "Ербол"},
    {"s_first": "Арсен", "s_last": "Султанов", "p_first": "Мурат"},
    {"s_first": "Мирас", "s_last": "Сапаров", "p_first": "Аскар"},
    {"s_first": "Бексултан", "s_last": "Исаев", "p_first": "Талгат"},
    {"s_first": "Ерасыл", "s_last": "Калиев", "p_first": "Нурлан"},
    {"s_first": "Нурдаулет", "s_last": "Аманжолов", "p_first": "Марат"},
    {"s_first": "Данияр", "s_last": "Болатов", "p_first": "Болат"},
    {"s_first": "Айбар", "s_last": "Сериков", "p_first": "Кайрат"},
    {"s_first": "Айдос", "s_last": "Нурланов", "p_first": "Даулет"},
    {"s_first": "Аружан", "s_last": "Смаилов", "p_first": "Жандос"},
    {"s_first": "Мадина", "s_last": "Алиев", "p_first": "Азамат"},
    {"s_first": "Айша", "s_last": "Омаров", "p_first": "Руслан"},
    {"s_first": "Томирис", "s_last": "Каримов", "p_first": "Арман"},
    {"s_first": "Амина", "s_last": "Ахметов", "p_first": "Болат"},
    {"s_first": "Амир", "s_last": "Ибрагимов", "p_first": "Мурат"}
]

MED_STUDENTS = [
    {"s_first": "Алия", "s_last": "Сапарова", "p_first": "Дамир"},
    {"s_first": "Гаухар", "s_last": "Касымова", "p_first": "Аскар"},
    {"s_first": "Мадина", "s_last": "Ахметова", "p_first": "Серик"},
    {"s_first": "Аружан", "s_last": "Исаева", "p_first": "Талгат"},
    {"s_first": "Жасмин", "s_last": "Султанова", "p_first": "Мурат"},
    {"s_first": "Камила", "s_last": "Оспанова", "p_first": "Ербол"},
    {"s_first": "Айша", "s_last": "Калиева", "p_first": "Нурлан"},
    {"s_first": "Айгерим", "s_last": "Болатова", "p_first": "Болат"},
    {"s_first": "Дана", "s_last": "Серикова", "p_first": "Кайрат"},
    {"s_first": "Анель", "s_last": "Алиева", "p_first": "Азамат"},
    {"s_first": "Сабина", "s_last": "Омарова", "p_first": "Руслан"},
    {"s_first": "Зере", "s_last": "Каримова", "p_first": "Арман"},
    {"s_first": "Райхан", "s_last": "Ахметова", "p_first": "Бауыржан"},
    {"s_first": "Назерке", "s_last": "Ибрагимова", "p_first": "Серик"},
    {"s_first": "Диана", "s_last": "Оспанова", "p_first": "Канат"},
    {"s_first": "Аяжан", "s_last": "Касымова", "p_first": "Ербол"},
    {"s_first": "Жансая", "s_last": "Султанова", "p_first": "Мурат"},
    {"s_first": "Данияр", "s_last": "Сапаров", "p_first": "Аскар"}
]

def run():
    print("=== НАЧАЛО СОЗДАНИЯ СВЯЗАННЫХ ГРУПП ===")
    
    # 1. Создаем кураторов
    c1_uid = create_or_get_user("nurlan.ospanov@gmail.com", "Нурлан Оспанов", "curator", "IT")
    db.reference(f"curators/{c1_uid}").update({
        "name": "Нурлан Оспанов",
        "email": "nurlan.ospanov@gmail.com",
        "profession": "IT"
    })
    
    c2_uid = create_or_get_user("madina.ibrahimova@gmail.com", "Мадина Ибрагимова", "curator", "Medicine")
    db.reference(f"curators/{c2_uid}").update({
        "name": "Мадина Ибрагимова",
        "email": "madina.ibrahimova@gmail.com",
        "profession": "Medicine"
    })
    
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    day_before = (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
    
    # Очищаем старых студентов в этих группах для корректной привязки
    db.reference(f"curators/{c1_uid}/students").delete()
    db.reference(f"curators/{c2_uid}/students").delete()
    
    # 2. Сеем группу IT
    print("\n[IT Группа] Создание 18 студентов и родителей...")
    for idx, s in enumerate(IT_STUDENTS):
        s_name = f"{s['s_first']} {s['s_last']}"
        s_email = f"{transliterate(s['s_first'])}.{transliterate(s['s_last'])}@gmail.com"
        
        p_name = f"{s['p_first']} {s['s_last']}"
        p_email = f"{transliterate(s['p_first'])}.{transliterate(s['s_last'])}@gmail.com"
        
        # Студент
        s_uid = create_or_get_user(s_email, s_name, "student", "IT")
        
        # Родитель
        p_uid = create_or_get_user(p_email, p_name, "parent", "IT", child_id=s_uid)
        
        pct = random.randint(72, 98)
        letter = "A" if pct >= 90 else "B" if pct >= 80 else "C" if pct >= 70 else "D"
        
        # Запись студента
        db.reference(f"students/{s_uid}").set({
            "name": s_name,
            "email": s_email,
            "profession": "IT",
            "curator_id": c1_uid,
            "parent_id": p_uid,
            "attendance": {
                day_before: random.choice([True, False]),
                yesterday: random.choice([True, False]),
                today: True
            },
            "grade": {"pct": pct, "letter": letter}
        })
        
        # Запись родителя
        db.reference(f"parents/{p_uid}").set({
            "name": p_name,
            "email": p_email,
            "child_id": s_uid
        })
        
        # Привязка к куратору
        db.reference(f"curators/{c1_uid}/students/{s_uid}").set(True)

    # 3. Сеем группу Medicine
    print("\n[Medicine Группа] Создание 18 студентов и родителей...")
    for idx, s in enumerate(MED_STUDENTS):
        s_name = f"{s['s_first']} {s['s_last']}"
        s_email = f"{transliterate(s['s_first'])}.{transliterate(s['s_last'])}@gmail.com"
        
        p_name = f"{s['p_first']} {s['s_last']}"
        p_email = f"{transliterate(s['p_first'])}.{transliterate(s['s_last'])}@gmail.com"
        
        # Студент
        s_uid = create_or_get_user(s_email, s_name, "student", "Medicine")
        
        # Родитель
        p_uid = create_or_get_user(p_email, p_name, "parent", "Medicine", child_id=s_uid)
        
        pct = random.randint(72, 98)
        letter = "A" if pct >= 90 else "B" if pct >= 80 else "C" if pct >= 70 else "D"
        
        # Запись студента
        db.reference(f"students/{s_uid}").set({
            "name": s_name,
            "email": s_email,
            "profession": "Medicine",
            "curator_id": c2_uid,
            "parent_id": p_uid,
            "attendance": {
                day_before: random.choice([True, False]),
                yesterday: random.choice([True, False]),
                today: True
            },
            "grade": {"pct": pct, "letter": letter}
        })
        
        # Запись родителя
        db.reference(f"parents/{p_uid}").set({
            "name": p_name,
            "email": p_email,
            "child_id": s_uid
        })
        
        # Привязка к куратору
        db.reference(f"curators/{c2_uid}/students/{s_uid}").set(True)

    # Обновляем счетчики кураторов
    c1_students = db.reference(f"curators/{c1_uid}/students").get() or {}
    db.reference(f"curators/{c1_uid}").update({"student_count": len(c1_students)})
    
    c2_students = db.reference(f"curators/{c2_uid}/students").get() or {}
    db.reference(f"curators/{c2_uid}").update({"student_count": len(c2_students)})

    print("\n=== ВСЕ ГРУППЫ УСПЕШНО СОЗДАНЫ И СВЯЗАНЫ! ===")
    print("Нурлан Оспанов (IT): 18 студентов")
    print("Мадина Ибрагимова (Medicine): 18 студентов")
    print("Все пароли: Kuraton2026!")

if __name__ == "__main__":
    run()
