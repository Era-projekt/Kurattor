import firebase_admin
from firebase_admin import credentials, db, auth
import random

# Инициализация Firebase
cred = credentials.Certificate("kuraton-firebase-adminsdk-fbsvc-a66f775d22.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://kuraton-default-rtdb.firebaseio.com'
    })

def update_alakankalan():
    email = "alakankalan@gmail.com"
    try:
        user_auth = auth.get_user_by_email(email)
        uid = user_auth.uid
        print(f"Найдено: {email} (UID: {uid})")

        # 1. Обновляем роль в /users/
        db.reference(f"users/{uid}").update({
            "role": "curator",
            "profession": "Design"
        })
        print("Роль в /users/ обновлена на curator.")

        # 2. Удаляем из /students/ (если был там)
        db.reference(f"students/{uid}").delete()
        print("Удален из /students/.")

        # 3. Находим 20 студентов Design для назначения
        all_students = db.reference("students").get() or {}
        design_students = []
        for sid, sdata in all_students.items():
            if sdata.get("profession") == "Design":
                design_students.append(sid)
        
        # Берем 20 штук (или сколько есть)
        to_assign = random.sample(design_students, min(len(design_students), 20))
        
        student_links = {}
        for sid in to_assign:
            student_links[sid] = True
            # Обновляем у студента curator_id
            db.reference(f"students/{sid}").update({"curator_id": uid})

        # 4. Создаем запись в /curators/
        db.reference(f"curators/{uid}").set({
            "name": "Аланкалан Айгүл Бекқызы",
            "email": email,
            "profession": "Design",
            "student_count": len(to_assign),
            "students": student_links
        })
        print(f"Запись в /curators/ создана. Назначено студентов: {len(to_assign)}")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    update_alakankalan()
