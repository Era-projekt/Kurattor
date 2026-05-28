import firebase_admin
from firebase_admin import auth, db
import datetime
from firebase_config import init_firebase

# Инициализация
init_firebase()

password = "Kuraton2026!"

def create_or_get_user(email, name, role, profession=None, child_id=None):
    try:
        user = auth.get_user_by_email(email)
        uid = user.uid
        print(f"Пользователь {email} уже существует с UID: {uid}")
    except Exception:
        user = auth.create_user(email=email, password=password, display_name=name)
        uid = user.uid
        print(f"Создан новый пользователь {email} с UID: {uid}")
    
    # Записываем в users
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

def run():
    print("=== НАЧАЛО СОЗДАНИЯ СВЯЗАННЫХ РОДИТЕЛЕЙ И СТУДЕНТОВ ===")
    
    # ── 1. Создаем кураторов ──
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
    
    # ── 2. Создаем студентов (без родителя пока) ──
    s1_uid = create_or_get_user("alibek.kasymov@gmail.com", "Алибек Касымов", "student", "IT")
    s2_uid = create_or_get_user("aliya.saparova@gmail.com", "Алия Сапарова", "student", "Medicine")
    
    # ── 3. Создаем родителей (привязанных к студентам) ──
    p1_uid = create_or_get_user("ospan.kasymov@gmail.com", "Оспан Касымов", "parent", "IT", child_id=s1_uid)
    p2_uid = create_or_get_user("damir.saparov@gmail.com", "Дамир Сапаров", "parent", "Medicine", child_id=s2_uid)
    
    # ── 4. Записываем данные студентов с parent_id и curator_id ──
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    day_before = (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
    
    db.reference(f"students/{s1_uid}").set({
        "name": "Алибек Касымов",
        "email": "alibek.kasymov@gmail.com",
        "profession": "IT",
        "curator_id": c1_uid,
        "parent_id": p1_uid,
        "attendance": {
            day_before: True,
            yesterday: False,
            today: True
        },
        "grade": {"pct": 94, "letter": "A"}
    })
    
    db.reference(f"students/{s2_uid}").set({
        "name": "Алия Сапарова",
        "email": "aliya.saparova@gmail.com",
        "profession": "Medicine",
        "curator_id": c2_uid,
        "parent_id": p2_uid,
        "attendance": {
            day_before: True,
            yesterday: True,
            today: True
        },
        "grade": {"pct": 98, "letter": "A"}
    })
    
    # ── 5. Записываем данные в parents ──
    db.reference(f"parents/{p1_uid}").set({
        "name": "Оспан Касымов",
        "email": "ospan.kasymov@gmail.com",
        "child_id": s1_uid
    })
    
    db.reference(f"parents/{p2_uid}").set({
        "name": "Дамир Сапаров",
        "email": "damir.saparov@gmail.com",
        "child_id": s2_uid
    })
    
    # ── 6. Привязываем студентов к кураторам ──
    db.reference(f"curators/{c1_uid}/students/{s1_uid}").set(True)
    c1_students = db.reference(f"curators/{c1_uid}/students").get() or {}
    db.reference(f"curators/{c1_uid}").update({"student_count": len(c1_students)})
    
    db.reference(f"curators/{c2_uid}/students/{s2_uid}").set(True)
    c2_students = db.reference(f"curators/{c2_uid}/students").get() or {}
    db.reference(f"curators/{c2_uid}").update({"student_count": len(c2_students)})
    
    print("\n=== ВСЕ АККАУНТЫ УСПЕШНО СОЗДАНЫ И СВЯЗАНЫ! ===")
    print("Пароль для всех: Kuraton2026!")

if __name__ == "__main__":
    run()
