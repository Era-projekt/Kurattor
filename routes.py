from flask import render_template, request, jsonify, session, redirect, url_for
from firebase_admin import auth, db
import functools
import datetime
import uuid
import openai
import random
import base64
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_token' not in session:
            return redirect(url_for('auth_page'))
        return f(*args, **kwargs)
    return decorated_function

def parent_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'parent' or 'child_id' not in session:
            return redirect(url_for('auth_page'))
        return f(*args, **kwargs)
    return decorated_function

def init_routes(app):
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB limit

    # ---------- Notification helper ----------
    def create_notification(uid, title, message, link=None):
        notif_id = str(uuid.uuid4())
        db.reference(f'notifications/{uid}/{notif_id}').set({
            'title': title,
            'message': message,
            'link': link or '',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'read': False
        })

    @app.context_processor
    def inject_user_avatar():
        avatar = None
        if 'uid' in session:
            try:
                user_data = db.reference(f"users/{session['uid']}").get() or {}
                avatar = user_data.get('avatar')
                session['avatar'] = avatar
            except Exception:
                pass
        return {'user_avatar': avatar}

    # ── Публичные страницы ─────────────────────────────────────────────────

    @app.route('/')
    def index():
        # Получаем кураторов для отображения на главной
        curators_ref = db.reference('curators').get() or {}
        grouped_curators = {}
        for cid, c in curators_ref.items():
            prof = c.get('profession', 'Other')
            if prof not in grouped_curators:
                grouped_curators[prof] = []
            c['id'] = cid
            grouped_curators[prof].append(c)
            
        return render_template('index.html', grouped_curators=grouped_curators)

    @app.route('/auth')
    def auth_page():
        if session.get('user_token'):
            role = session.get('role', '')
            return redirect(url_for('student_dashboard_view' if role == 'student' else 'curator_dashboard_view' if role == 'curator' else 'parent_dashboard_view'))
        return render_template('auth.html')

    @app.route('/register/student')
    def register_student():
        return render_template('register_student.html')

    @app.route('/register/curator')
    def register_curator():
        return render_template('register_curator.html')

    @app.route('/register/parent')
    def register_parent():
        return render_template('register_parent.html')

    @app.route('/search')
    def search_page():
        return render_template('search.html')

    # ── Auth API ───────────────────────────────────────────────────────────

    @app.route('/api/login', methods=['POST'])
    def api_login():
        """Проверяет Firebase JWT токен или локальный пароль и сохраняет сессию."""
        data = request.json
        id_token = data.get('idToken')
        email = data.get('email')
        password = data.get('password')

        # Локальный вход по email и паролю
        if email and password:
            try:
                all_users = db.reference('users').get() or {}
                found_uid = None
                found_user_data = None
                for uid, udata in all_users.items():
                    if udata.get('email', '').strip().lower() == email.strip().lower():
                        found_uid = uid
                        found_user_data = udata
                        break
                
                if found_uid and found_user_data:
                    stored_pwd = found_user_data.get('password', 'Kuraton2026!')
                    if stored_pwd == password:
                        session['user_token'] = 'mock_token_' + found_uid
                        session['uid'] = found_uid
                        session['role'] = found_user_data.get('role')
                        session['user_name'] = found_user_data.get('name', 'User')
                        
                        if session['role'] == 'parent':
                            session['child_id'] = found_user_data.get('child_id')
                            return jsonify({'success': True, 'redirect': url_for('parent_dashboard_view')})
                        elif session['role'] == 'student':
                            return jsonify({'success': True, 'redirect': url_for('student_dashboard_view')})
                        elif session['role'] == 'curator':
                            return jsonify({'success': True, 'redirect': url_for('curator_dashboard_view')})
                    else:
                        return jsonify({'success': False, 'error': 'Неверный пароль'})
                
                return jsonify({'success': False, 'error': 'Пользователь с таким email не найден'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        # Исходный вход по Firebase JWT токену
        try:
            decoded = auth.verify_id_token(id_token)
            uid = decoded['uid']
            session['user_token'] = id_token
            session['uid'] = uid

            user_ref = db.reference(f'users/{uid}')
            user_data = user_ref.get()

            if user_data:
                session['role'] = user_data.get('role')
                session['user_name'] = user_data.get('name', 'User')
                if session['role'] == 'parent':
                    session['child_id'] = user_data.get('child_id')
                    return jsonify({'success': True, 'redirect': url_for('parent_dashboard_view')})
                elif session['role'] == 'student':
                    return jsonify({'success': True, 'redirect': url_for('student_dashboard_view')})
                elif session['role'] == 'curator':
                    return jsonify({'success': True, 'redirect': url_for('curator_dashboard_view')})

            return jsonify({'success': False, 'error': 'Пользователь не найден в базе данных'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/register', methods=['POST'])
    def api_register():
        """Сохраняет дополнительные данные нового пользователя в БД."""
        data = request.json
        uid        = data.get('uid')
        role       = data.get('role')
        name       = data.get('name')
        profession = data.get('profession')
        email      = data.get('email')
        password   = data.get('password')
        curator_id = data.get('curator_id')
        child_id   = data.get('child_id')

        try:
            # ── Специальная логика для родителей (One-to-One) ──
            if role == 'parent' and child_id:
                # Проверяем, нет ли уже родителя у этого ребенка
                student_ref = db.reference(f'students/{child_id}')
                student_data = student_ref.get()
                if not student_data:
                    return jsonify({'success': False, 'error': 'Выбранный студент не найден в базе'})
                
                if student_data.get('parent_id'):
                    return jsonify({'success': False, 'error': 'Для данного студента уже зарегистрирован родительский аккаунт'})

            # ── Общее сохранение в users ──
            db.reference(f'users/{uid}').set({
                'name': name, 'role': role,
                'profession': profession, 'email': email,
                'password': password or 'Kuraton2026!',
                'child_id': child_id if role == 'parent' else None
            })

            if role == 'curator':
                db.reference(f'curators/{uid}').set({
                    'name': name, 'email': email,
                    'profession': profession, 'student_count': 0
                })
            elif role == 'student':
                student_ref = db.reference(f'students/{uid}')
                student_data = {
                    'name': name, 'email': email,
                    'profession': profession, 'curator_id': curator_id,
                    'attendance': {}, 'grade': {'pct': 0, 'letter': '—'}
                }
                student_ref.set(student_data)
                
                if curator_id:
                    c_ref = db.reference(f'curators/{curator_id}')
                    c_data = c_ref.get() or {}
                    current_count = c_data.get('student_count', 0)
                    if current_count < 20:
                        db.reference(f'curators/{curator_id}/students/{uid}').set(True)
                        c_ref.update({'student_count': current_count + 1})
            
            elif role == 'parent':
                # Сохраняем в таблицу родителей
                db.reference(f'parents/{uid}').set({
                    'name': name, 'email': email, 'child_id': child_id
                })
                # Устанавливаем обратную связь в таблице студентов
                db.reference(f'students/{child_id}').update({
                    'parent_id': uid
                })

            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))

    @app.route('/api/new_semester', methods=['POST'])
    @login_required
    def new_semester():
        if session.get('role') != 'curator':
            return jsonify({'success': False, 'error': 'Доступ запрещен'})
        
        cid = session.get('uid')
        try:
            curator_data = db.reference(f'curators/{cid}').get() or {}
            student_ids = curator_data.get('students', {})
            for sid in student_ids.keys():
                # Wipe attendance
                db.reference(f'students/{sid}/attendance').delete()
                # Wipe daily marks
                db.reference(f'students/{sid}/daily_marks').delete()
                # Reset grade
                db.reference(f'students/{sid}/grade').set({'pct': 0, 'letter': '—'})
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    # ── Кабинет студента ───────────────────────────────────────────────────

    @app.route('/student')
    @login_required
    def student_page():
        if session.get('role') != 'student':
            return redirect(url_for('index'))

        uid          = session['uid']
        student_data = db.reference(f'students/{uid}').get() or {}
        user_data    = db.reference(f'users/{uid}').get() or {}
        
        att = student_data.get('attendance', {})
        attended_count = sum(1 for v in att.values() if v)
        absences_count = sum(1 for v in att.values() if not v)

        curator = None
        if student_data.get('curator_id'):
            curator = db.reference(f"users/{student_data['curator_id']}").get()

        # Check for pending request
        pending_request = None
        all_requests = db.reference('requests').get() or {}
        for cid, requests in all_requests.items():
            if uid in requests:
                curator_info = db.reference(f"users/{cid}").get() or {}
                pending_request = {
                    'curator_id': cid,
                    'curator_name': curator_info.get('name', '—'),
                    'status': 'pending'
                }
                break

        # Find parent (Optimized)
        parent = None
        parent_id = student_data.get('parent_id')
        if parent_id:
            parent = db.reference(f'parents/{parent_id}').get()

        return render_template('student_dashboard.html',
                               student=student_data, user=user_data, curator=curator, 
                               parent=parent,
                               pending_request=pending_request,
                               attended_count=attended_count,
                               absences_count=absences_count)

    # ── Кабинет куратора ───────────────────────────────────────────────────

    @app.route('/curator')
    @login_required
    def curator_page():
        if session.get('role') != 'curator':
            return redirect(url_for('index'))

        uid          = session['uid']
        user_data    = db.reference(f'users/{uid}').get() or {}
        curator_data = db.reference(f'curators/{uid}').get() or {}

        # Calculate detailed statistics
        all_student_data = []
        unique_dates     = set()
        total_misses     = 0
        students_list    = []
        
        student_ids = curator_data.get('students', {})
        for sid in student_ids.keys():
            sdata = db.reference(f'students/{sid}').get() or {}
            if sdata:
                att = sdata.get('attendance', {})
                absences = sum(1 for v in att.values() if not v)
                present_cnt = sum(1 for v in att.values() if v)
                total_cnt   = len(att)
                total_misses += absences
                
                for d in att.keys():
                    unique_dates.add(d)
                
                # Find student parent (Optimized)
                s_parent = None
                p_id = sdata.get('parent_id')
                if p_id:
                    s_parent = db.reference(f'parents/{p_id}').get()

                students_list.append({
                    'uid': sid, 'name': sdata.get('name', '—'),
                    'email': sdata.get('email', '—'),
                    'absences': absences, 'attended': present_cnt, 'total_att': total_cnt,
                    'parent': s_parent
                })
                all_student_data.append(sdata)

        # Average absences per student
        total_students = len(students_list)
        avg_absences = round(total_misses / total_students, 1) if total_students else 0

        # Get incoming requests
        incoming_requests = []
        req_ref = db.reference(f'requests/{uid}')
        req_data = req_ref.get() or {}
        for rsid, details in req_data.items():
            incoming_requests.append({
                'student_id': rsid,
                'name': details.get('name', '—'),
                'email': details.get('email', '—'),
                'profession': details.get('profession', '—')
            })

        # Risk group (absences > 2)
        low_attendance_list = []
        for s in students_list:
            if s['absences'] > 2:
                low_attendance_list.append(s)

        today = datetime.date.today().strftime("%Y-%m-%d")
        return render_template('curator_dashboard.html',
                               curator=curator_data, user=user_data,
                               students_list=students_list, 
                               low_attendance_list=low_attendance_list,
                               today_date=today,
                               incoming_requests=incoming_requests,
                               avg_absences=avg_absences,
                               total_misses=total_misses)

    @app.route('/student/view/<sid>')
    @login_required
    def view_student_profile(sid):
        """Позволяет куратору просматривать профиль студента с его расписанием."""
        s_data = db.reference(f'students/{sid}').get()
        if not s_data:
            return "Студент не найден", 404
        
        # Получаем расписание по специальности студента
        profession = s_data.get('profession', 'IT')
        spec_schedule = db.reference(f'specialty_schedules/{profession}').get() or {}
        
        # Данные текущего куратора для боковой панели
        uid = session.get('uid')
        user_data = db.reference(f'users/{uid}').get() or {}
        
        return render_template('student_view.html', 
                               sdata=s_data, 
                               schedule=spec_schedule, 
                               user=user_data)


    # ── Назначение куратора ────────────────────────────────────────────────

    # ── Система запросов (Student -> Curator) ─────────────────────────────────

    @app.route('/api/send_request', methods=['POST'])
    @login_required
    def send_request():
        data = request.json
        curator_id = data.get('curator_id')
        student_id = session.get('uid')
        
        if not curator_id:
            return jsonify({'success': False, 'error': 'ID куратора не указан'})

        try:
            student_user = db.reference(f'users/{student_id}').get()
            db.reference(f'requests/{curator_id}/{student_id}').set({
                'name': student_user.get('name'),
                'email': student_user.get('email'),
                'profession': student_user.get('profession'),
                'timestamp': datetime.datetime.now().isoformat()
            })
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/cancel_request', methods=['POST'])
    @login_required
    def cancel_request():
        data = request.json
        curator_id = data.get('curator_id')
        student_id = session.get('uid')
        try:
            db.reference(f'requests/{curator_id}/{student_id}').delete()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/respond_request', methods=['POST'])
    @login_required
    def respond_request():
        """Куратор принимает или отклоняет запрос."""
        data = request.json
        student_id = data.get('student_id')
        action     = data.get('action') # 'approve' or 'reject'
        curator_id = session.get('uid')
        MAX        = 20

        if not student_id or not action:
            return jsonify({'success': False, 'error': 'Данные неполные'})

        try:
            # Всегда удаляем запрос из очереди
            db.reference(f'requests/{curator_id}/{student_id}').delete()

            if action == 'approve':
                cur_ref = db.reference(f'curators/{curator_id}')
                cdata   = cur_ref.get()
                
                if cdata.get('student_count', 0) >= MAX:
                    return jsonify({'success': False, 'error': 'У вас больше нет свободных мест'})

                # 1. Обновляем куратора
                next_count = cdata.get('student_count', 0) + 1
                cur_ref.update({'student_count': next_count})
                db.reference(f'curators/{curator_id}/students/{student_id}').set(True)

                # 2. Обновляем студента
                db.reference(f'students/{student_id}').update({'curator_id': curator_id})
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    # ── Сохранение посещаемости ────────────────────────────────────────────

    @app.route('/api/save_attendance', methods=['POST'])
    @login_required
    def save_attendance():
        """Куратор сохраняет посещаемость студентов за СЕГОДНЯШНЮЮ дату."""
        data    = request.json
        # Принудительно устанавливаем сегодняшнюю дату
        date    = datetime.date.today().isoformat()
        updates = data.get('attendance', {}) # {sid: bool}
        
        # Sunday check для надежности
        if datetime.date.today().weekday() == 6:
            return jsonify({'success': False, 'error': 'Нельзя отмечать посещаемость в воскресенье'})

        try:
            for sid, present in updates.items():
                db.reference(f'students/{sid}/attendance/{date}').set(bool(present))
            return jsonify({'success': True, 'date': date})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/get_attendance_by_date', methods=['GET'])
    @login_required
    def get_attendance_by_date():
        """Возвращает посещаемость и оценки всех студентов куратора на конкретный день."""
        date       = request.args.get('date')
        curator_id = session.get('uid')
        if not date: return jsonify({'success': False, 'error': 'Дата не указана'})
        
        curator_data = db.reference(f'curators/{curator_id}').get() or {}
        student_ids  = curator_data.get('students', {})
        attendance   = {}
        daily_marks  = {}
        
        for sid in student_ids.keys():
            # Посещаемость
            att = db.reference(f'students/{sid}/attendance/{date}').get()
            attendance[sid] = att
            # Оценка (daily)
            mark = db.reference(f'students/{sid}/daily_marks/{date}').get() or '—'
            daily_marks[sid] = mark
            
        return jsonify({'success': True, 'attendance': attendance, 'grades': daily_marks})

    @app.route('/api/set_manual_grade', methods=['POST'])
    @login_required
    def set_manual_grade():
        """Куратор вручную выставляет буквенную оценку за КОНКРЕТНЫЙ день."""
        data       = request.json
        student_id = data.get('studentId')
        letter     = data.get('letter')
        date       = data.get('date')
        
        if not date:
            return jsonify({'success': False, 'error': 'Дата не указана'})

        try:
            # Sunday check
            dt = datetime.datetime.strptime(date, '%Y-%m-%d')
            if dt.weekday() == 6:
                return jsonify({'success': False, 'error': 'Нельзя ставить оценки в воскресенье'})

            # Сохраняем оценку за день
            db.reference(f'students/{student_id}/daily_marks/{date}').set(letter)
            
            # Обновляем итоговую для совместимости
            db.reference(f'students/{student_id}/grade').update({
                'letter': letter
            })
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/issue_grade_self', methods=['POST'])
    @login_required
    def issue_grade_self():
        """Студент сам пересчитывает свою итоговую оценку."""
        uid = session.get('uid')
        try:
            sdata   = db.reference(f'students/{uid}').get() or {}
            att     = sdata.get('attendance', {})
            total   = len(att)
            present = sum(1 for v in att.values() if v) if total else 0
            pct     = round((present / total) * 100) if total else 0
            if pct >= 90:   letter, gpa = "A", 4.0
            elif pct >= 80: letter, gpa = "B", 3.0
            elif pct >= 70: letter, gpa = "C", 2.0
            elif pct >= 60: letter, gpa = "D", 1.0
            else:           letter, gpa = "F", 0.0
            grade = {'pct': pct, 'letter': letter}
            db.reference(f'students/{uid}/grade').set(grade)
            return jsonify({'success': True, 'grade': grade})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    # ── Выдача / пересчёт оценки куратором ────────────────────────────────────


    @app.route('/api/issue_grade', methods=['POST'])
    @login_required
    def issue_grade():
        """Пересчитывает итоговую оценку студента на основе посещаемости."""
        data       = request.json
        student_id = data.get('studentId')
        try:
            sdata    = db.reference(f'students/{student_id}').get() or {}
            att      = sdata.get('attendance', {})
            total    = len(att)
            present  = sum(1 for v in att.values() if v) if total else 0
            pct      = round((present / total) * 100) if total else 0

            if pct >= 90:   letter, gpa = "A",  4.0
            elif pct >= 80: letter, gpa = "B",  3.0
            elif pct >= 70: letter, gpa = "C",  2.0
            elif pct >= 60: letter, gpa = "D",  1.0
            else:           letter, gpa = "F",  0.0

            grade = {'pct': pct, 'letter': letter}
            db.reference(f'students/{student_id}/grade').set(grade)
            return jsonify({'success': True, 'grade': grade})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    # ── Поиск пользователей ────────────────────────────────────────────────

    # ── Расписание (Schedule) ──────────────────────────────────────────────
    @app.route('/api/get_schedule', methods=['GET'])
    @login_required
    def get_schedule():
        # Расписание теперь привязано к специальности (profession)
        uid  = session.get('uid')
        user_data = db.reference(f'users/{uid}').get() or {}
        profession = user_data.get('profession', 'IT') # По умолчанию IT
        
        print(f"DEBUG: Запрос расписания для специальности: {profession}")
        sched = db.reference(f'specialty_schedules/{profession}').get() or {}
        return jsonify({'schedule': sched})

    @app.route('/api/save_lesson', methods=['POST'])
    @login_required
    def save_lesson():
        if session.get('role') != 'curator': return jsonify({'success': False})
        cid  = session.get('uid')
        data = request.json
        day  = data.get('day') # 'mon','tue',...
        time = data.get('time')
        subject = data.get('subject')
        room    = data.get('room', '')
        
        db.reference(f'schedules/{cid}/{day}/{time.replace(":","-")}').set({
            'subject': subject, 'time': time, 'room': room
        })
        return jsonify({'success': True})

    @app.route('/api/delete_lesson', methods=['POST'])
    @login_required
    def delete_lesson():
        if session.get('role') != 'curator': return jsonify({'success': False})
        cid  = session.get('uid')
        data = request.json
        day  = data.get('day')
        time = data.get('time')
        
        db.reference(f'schedules/{cid}/{day}/{time.replace(":","-")}').delete()
        return jsonify({'success': True})

    # ── Файлы (Library) ───────────────────────────────────────────────────
    @app.route('/api/get_files', methods=['GET'])
    @login_required
    def get_files():
        # Accessible to everyone: both students and curators
        files = db.reference('files').get() or {}
        
        # Handle both dict and list from Firebase RTDB
        result = []
        if isinstance(files, dict):
            for k, v in files.items():
                if isinstance(v, dict): result.append({'id': k, **v})
        elif isinstance(files, list):
            for i, v in enumerate(files):
                if v and isinstance(v, dict): result.append({'id': i, **v})
                
        return jsonify(result)

    @app.route('/api/upload_file', methods=['POST'])
    @login_required
    def upload_file():
        if session.get('role') != 'curator': return jsonify({'success': False})
        data = request.json
        file_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        db.reference(f'files/{file_id}').set({
            'name': data.get('name'), 'url': data.get('url'),
            'type': data.get('type'), 'date': datetime.date.today().isoformat()
        })
        return jsonify({'success': True})

    @app.route('/api/delete_file', methods=['POST'])
    @login_required
    def delete_file():
        if session.get('role') != 'curator': return jsonify({'success': False})
        fid = request.json.get('fileId')
        if fid:
            db.reference(f'files/{fid}').delete()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'No file ID'})

    # ── Чат (Chat) ────────────────────────────────────────────────────────
    @app.route('/api/get_chat', methods=['GET'])
    @login_required
    def get_chat():
        room_id = request.args.get('room') # 'group', 'private', or a student's UID
        uid = session.get('uid')
        role = session.get('role')
        
        if role == 'student':
            s_data = db.reference(f'students/{uid}').get() or {}
            cid = s_data.get('curator_id', 'no_curator')
            if room_id == 'group':
                room_path = f'chats/{cid}/group'
            elif room_id == 'private':
                room_path = f'chats/private/{uid}'
            else:
                # Student to student direct chat!
                sorted_uids = sorted([uid, room_id])
                room_path = f'chats/direct/{sorted_uids[0]}_{sorted_uids[1]}'
        else:
            # Curator viewing
            if room_id == 'group':
                room_path = f'chats/{uid}/group'
            else:
                room_path = f'chats/private/{room_id}'
            
        messages = db.reference(room_path).order_by_key().limit_to_last(50).get() or {}
        return jsonify({'messages': messages})

    @app.route('/api/send_message', methods=['POST'])
    @login_required
    def send_message():
        data = request.json
        room_id = data.get('room') # 'group', 'private', or student's UID
        text = data.get('text', '').strip()
        if not text: return jsonify({'success': False})
        
        uid = session.get('uid')
        role = session.get('role')
        user_name = session.get('user_name')
        
        # Fallback if name is missing from session
        if not user_name:
            user_data = db.reference(f'users/{uid}').get() or {}
            user_name = user_data.get('name', 'User')
            session['user_name'] = user_name

        if role == 'student':
            s_data = db.reference(f'students/{uid}').get() or {}
            cid = s_data.get('curator_id')
            if room_id == 'group':
                if not cid: return jsonify({'success': False, 'error': 'No curator'})
                room_path = f'chats/{cid}/group'
            elif room_id == 'private':
                room_path = f'chats/private/{uid}'
            else:
                # Student to student direct chat!
                sorted_uids = sorted([uid, room_id])
                room_path = f'chats/direct/{sorted_uids[0]}_{sorted_uids[1]}'
        else:
            # Curator sending
            if room_id == 'group':
                room_path = f'chats/{uid}/group'
            else:
                room_path = f'chats/private/{room_id}'
            
        msg_ref = db.reference(room_path).push()
        msg_ref.set({
            'sender_id': uid, 'sender_name': user_name, 'role': role,
            'text': text, 'timestamp': datetime.datetime.now().isoformat()
        })
        return jsonify({'success': True})

    # ── Уведомления и Предупреждения (Notifications & Warnings) ─────────────
    @app.route('/api/send_notification', methods=['POST'])
    @login_required
    def send_notification():
        if session.get('role') != 'curator': return jsonify({'success': False})
        data = request.json
        sid = data.get('studentId')
        msg = data.get('message')
        type = data.get('type', 'info') # 'info','warning','urgent'
        
        ref = db.reference(f'notifications/{sid}').push()
        ref.set({
            'message': msg, 'type': type, 'date': datetime.date.today().isoformat(), 'read': False
        })
        return jsonify({'success': True})

    @app.route('/api/get_notifications', methods=['GET'])
    @login_required
    def get_notifications():
        uid = session.get('uid')
        notes = db.reference(f'notifications/{uid}').get() or {}
        return jsonify(list(notes.values())[::-1])

    @app.route('/api/search_users', methods=['GET'])
    def search_users():
        query = request.args.get('q', '').lower().strip()
        if not query or len(query) < 2:
            return jsonify([])

        all_users = db.reference('users').get() or {}
        results = []
        for uid, udata in all_users.items():
            name  = udata.get('name', '')
            prof  = udata.get('profession', '')
            email = udata.get('email', '')
            if (query in name.lower() or
                query in prof.lower() or
                query in email.lower()):
                results.append({
                    'uid':        uid,
                    'name':       name,
                    'role':       udata.get('role', ''),
                    'profession': prof,
                })
        return jsonify(results[:30])  # максимум 30 результатов

    @app.route('/api/get_curators', methods=['POST'])
    def get_curators():
        """Возвращает список свободных кураторов по специальности."""
        data = request.json
        profession = data.get('profession', '').strip().lower()
        
        all_curators = db.reference('curators').get() or {}
        results = []
        
        for cid, cdata in all_curators.items():
            c_prof = cdata.get('profession', '').strip().lower()
            count = cdata.get('student_count', 0)
            
            if c_prof == profession and count < 20:
                results.append({
                    'id': cid,
                    'name': cdata.get('name', 'Unknown'),
                    'student_count': count,
                    'max': 20
                })
        
        return jsonify({'curators': results})

    @app.route('/api/get_students_by_profession', methods=['POST'])
    def get_students_by_profession():
        """Возвращает список студентов по выбранной специальности, у которых ЕЩЕ НЕТ родителя."""
        data = request.json
        profession = data.get('profession', '').strip().lower()
        
        all_students = db.reference('students').get() or {}
        results = []
        
        for sid, sdata in all_students.items():
            s_prof = sdata.get('profession', '').strip().lower()
            # Проверяем специальность и отсутствие привязанного родителя
            if s_prof == profession and not sdata.get('parent_id'):
                results.append({
                    'id': sid,
                    'name': sdata.get('name', 'Unknown')
                })
        
        return jsonify({'students': results})

    # ── Родительский кабинет ────────────────────────────────────────────────
    @app.route('/parent/access/<token>')
    def parent_access(token):
        """Вход родителя по токену."""
        sid = db.reference(f'parent_links/{token}').get()
        if not sid:
            return "Неверный или просроченный токен доступа", 403
        
        session['role'] = 'parent'
        session['child_id'] = sid
        session['user_name'] = "Родитель"
        return redirect(url_for('parent_dashboard_view'))

    @app.route('/parent/dashboard')
    @parent_required
    def parent_dashboard():
        """Отображение данных ребенка для родителя."""
        sid = session.get('child_id')
        sdata = db.reference(f'students/{sid}').get()
        if not sdata:
            return "Данные ребенка не найдены", 404
        
        # Получаем расписание
        profession = sdata.get('profession', 'IT')
        schedule = db.reference(f'specialty_schedules/{profession}').get() or {}
        
        return render_template('parent_dashboard.html', sdata=sdata, schedule=schedule)

    # ── Дополнительные API функции (Аватар, Пароль, Друзья) ──────────────────────────

    @app.route('/api/update_avatar', methods=['POST'])
    @login_required
    def update_avatar():
        data = request.json
        avatar_base64 = data.get('avatar')
        uid = session.get('uid')
        if not avatar_base64:
            return jsonify({'success': False, 'error': 'Изображение не получено'})
        try:
            db.reference(f'users/{uid}').update({'avatar': avatar_base64})
            role = session.get('role')
            if role == 'student':
                db.reference(f'students/{uid}').update({'avatar': avatar_base64})
            elif role == 'curator':
                db.reference(f'curators/{uid}').update({'avatar': avatar_base64})
            session['avatar'] = avatar_base64
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/change_password', methods=['POST'])
    @login_required
    def change_password():
        data = request.json
        old_password = data.get('oldPassword')
        new_password = data.get('newPassword')
        uid = session.get('uid')
        
        if not old_password or not new_password:
            return jsonify({'success': False, 'error': 'Заполните все поля'})
            
        try:
            user_ref = db.reference(f'users/{uid}')
            user_data = user_ref.get()
            if not user_data:
                return jsonify({'success': False, 'error': 'Пользователь не найден'})
            stored_pwd = user_data.get('password', 'Kuraton2026!')
            if stored_pwd != old_password:
                return jsonify({'success': False, 'error': 'Неверный старый пароль'})
            user_ref.update({'password': new_password})
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/add_friend', methods=['POST'])
    @login_required
    def add_friend():
        data = request.json
        friend_uid = data.get('friendUid')
        my_uid = session.get('uid')
        
        if not friend_uid or friend_uid == my_uid:
            return jsonify({'success': False, 'error': 'Некорректный ID пользователя'})
            
        try:
            db.reference(f'friends/{my_uid}/{friend_uid}').set(True)
            db.reference(f'friends/{friend_uid}/{my_uid}').set(True)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/get_friends', methods=['GET'])
    @login_required
    def get_friends():
        my_uid = session.get('uid')
        try:
            friends_ref = db.reference(f'friends/{my_uid}').get() or {}
            result = []
            for friend_uid in friends_ref.keys():
                u_data = db.reference(f'users/{friend_uid}').get()
                if u_data:
                    result.append({
                        'uid': friend_uid,
                        'name': u_data.get('name', 'User'),
                        'avatar': u_data.get('avatar', ''),
                        'role': u_data.get('role', 'student'),
                        'profession': u_data.get('profession', '')
                    })
            return jsonify({'success': True, 'friends': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    # ── Library API ────────────────────────────────────────────────────────
    import base64, random, datetime
    from flask import Response, redirect

    @app.route('/library')
    @login_required
    def library_page():
        return render_template('library.html')

    @app.route('/api/is_curator')
    @login_required
    def api_is_curator():
        return jsonify({'is_curator': session.get('role') == 'curator'})

    @app.route('/api/get_materials')
    @login_required
    def api_get_materials():
        try:
            files_ref = db.reference('files')
            data = files_ref.get() or {}
            materials = []
            for fid, info in data.items():
                materials.append({
                    'id': fid,
                    'name': info.get('name'),
                    'type': info.get('type'),
                    'specialty': info.get('specialty'),
                    'url': info.get('url') or f"/api/download_material/{fid}"
                })
            return jsonify({'materials': materials})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/download_material/<fid>')
    @login_required
    def api_download_material(fid):
        try:
            info = db.reference(f'files/{fid}').get()
            if not info:
                return jsonify({'error': 'File not found'}), 404
            if 'data' in info:
                content = base64.b64decode(info['data'])
                resp = Response(content, mimetype='application/octet-stream')
                resp.headers.set('Content-Disposition', 'attachment', filename=info.get('name', 'material'))
                return resp
            if 'url' in info:
                return redirect(info['url'])
            return jsonify({'error': 'No downloadable content'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/upload_material', methods=['POST'])
    @login_required
    def api_upload_material():
        if session.get('role') != 'curator':
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        file_obj = request.files['file']
        specialty = request.form.get('specialty', 'General')
        filename = file_obj.filename
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        data_bytes = file_obj.read()
        b64_data = base64.b64encode(data_bytes).decode('utf-8')
        file_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1000, 9999))
        db.reference('files').child(file_id).set({
            'name': filename,
            'type': ext,
            'specialty': specialty,
            'uploaded_by': session.get('uid'),
            'data': b64_data,
            'date': datetime.date.today().isoformat()
        })
        return jsonify({'success': True, 'message': 'Material uploaded'}), 200

    # ---------- Notification Endpoints ----------
    @app.route('/api/get_notifications', methods=['GET'])
    @login_required
    def api_get_notifications():
        uid = session.get('uid')
        if not uid:
            return jsonify({'success': False, 'error': 'Unauthenticated'}), 401
        notifs_ref = db.reference(f'notifications/{uid}').get() or {}
        notif_list = []
        unread_count = 0
        for nid, data in notifs_ref.items():
            notif = {'id': nid, 'title': data.get('title'), 'message': data.get('message'), 'link': data.get('link'), 'timestamp': data.get('timestamp'), 'read': data.get('read', False)}
            if not notif['read']:
                unread_count += 1
            notif_list.append(notif)
        notif_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return jsonify({'success': True, 'notifications': notif_list, 'unread_count': unread_count})

    @app.route('/api/mark_notification_read', methods=['POST'])
    @login_required
    def api_mark_notification_read():
        uid = session.get('uid')
        data = request.json
        notif_id = data.get('notification_id')
        if not uid or not notif_id:
            return jsonify({'success': False, 'error': 'Invalid request'}), 400
        try:
            db.reference(f'notifications/{uid}/{notif_id}/read').set(True)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/mark_absent', methods=['POST'])
    @login_required
    def api_mark_absent():
        if session.get('role') != 'curator':
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        data = request.json
        student_uid = data.get('student_uid')
        date_str = data.get('date') or datetime.date.today().isoformat()
        reason = data.get('reason', '')
        if not student_uid:
            return jsonify({'success': False, 'error': 'student_uid required'}), 400
        db.reference(f'absences/{student_uid}/{date_str}').set({'reason': reason, 'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'})
        student_data = db.reference(f'students/{student_uid}').get() or {}
        parent_uid = student_data.get('parent_id')
        if parent_uid:
            create_notification(parent_uid, 'Балаңыз сабаққа келе алмайды', f'Балаңыз {date_str} күні сабаққа келмеді. Себебі: {reason}')
        return jsonify({'success': True})

    @app.route('/api/upload_material', methods=['POST'])
    @login_required
    def api_upload_material_with_notify():
        if session.get('role') != 'curator':
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        file_obj = request.files['file']
        specialty = request.form.get('specialty', 'General')
        filename = file_obj.filename
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        data_bytes = file_obj.read()
        b64_data = base64.b64encode(data_bytes).decode('utf-8')
        file_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1000, 9999))
        db.reference('files').child(file_id).set({
            'name': filename,
            'type': ext,
            'specialty': specialty,
            'uploaded_by': session.get('uid'),
            'data': b64_data,
            'date': datetime.date.today().isoformat()
        })
        users = db.reference('users').get() or {}
        for uid, udata in users.items():
            if udata.get('role') == 'student':
                create_notification(uid, 'Жаңа материал қосылды', f'Жаңа материал "{filename}" қосылды')
        return jsonify({'success': True, 'message': 'Material uploaded'}), 200

    @app.route('/api/ai_query', methods=['POST'])
    @login_required
    def api_ai_query():
        data = request.json
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt required'}), 400
        try:
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.7
            )
            answer = response.choices[0].message.content.strip()
            return jsonify({'success': True, 'answer': answer})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # ---------- Dashboard Routes ----------
    @app.route('/curator_dashboard')
    @login_required
    def curator_dashboard_view():
        if session.get('role') != 'curator':
            return redirect(url_for('auth_page'))
        return redirect(url_for('curator_page'))

    @app.route('/student_dashboard')
    @login_required
    def student_dashboard_view():
        if session.get('role') != 'student':
            return redirect(url_for('auth_page'))
        return redirect(url_for('student_page'))

    @app.route('/parent_dashboard')
    @login_required
    def parent_dashboard_view():
        if session.get('role') != 'parent':
            return redirect(url_for('auth_page'))
        return redirect(url_for('parent_dashboard'))
