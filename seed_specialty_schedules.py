from firebase_config import init_firebase
from firebase_admin import db
import json

def seed_schedules():
    init_firebase()
    print("=== ГЕНЕРАЦИЯ УЧЕБНЫХ ПЛАНОВ ПО СПЕЦИАЛЬНОСТЯМ ===")
    
    # 6-day (mon-sat)
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat']
    times = ["09:00", "10:30", "12:00", "13:30"] # 4 slots = 6 hours total with breaks
    
    specialties = {
        "IT": ["Алгоритмы", "Python Dev", "Базы данных", "Сетевое администрирование", "Кибербезопасность"],
        "Economics": ["Макроэкономика", "Бухучет", "Менеджмент", "Аудит", "Финансы"],
        "Medicine": ["Анатомия", "Гигиена", "Фармакология", "Хирургия", "Терапия", "Лабораторные"],
        "Law": ["Гражданское право", "Уголовное право", "Конституция РК", "Логика", "Международное право"],
        "Design": ["Рисунок", "Типографика", "UX/UI Design", "История искусств", "3D Modeling"]
    }
    
    rooms = ["101", "204", "305", "402", "510", "Аудитория А", "Зал №3"]
    
    for spec, subjects in specialties.items():
        print(f"-> Создаю расписание для: {spec}")
        spec_sched = {}
        
        for d in days:
            day_data = {}
            # Randomly pick 4 subjects for the day
            day_subjects = subjects[:]
            import random
            random.shuffle(day_subjects)
            
            for t_idx, time_str in enumerate(times):
                subj = day_subjects[t_idx % len(day_subjects)]
                day_data[time_str.replace(":", "-")] = {
                    "subject": f"{subj} ({'Лекция' if t_idx < 2 else 'Практика'})",
                    "room": random.choice(rooms),
                    "time": time_str
                }
            spec_sched[d] = day_data
            
        db.reference(f"specialty_schedules/{spec}").set(spec_sched)
    
    print("\n[DONE] Все учебные планы загружены в базу!")

if __name__ == "__main__":
    seed_schedules()
