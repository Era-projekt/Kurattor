from flask import render_template, request, jsonify, session, redirect, url_for
from firebase_admin import auth, db
import functools
import datetime

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
            return redirect(url_for('student_dashboard' if role == 'student' else 'curator_dashboard' if role == 'curator' else 'parent_dashboard'))
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
        """Проверяет Firebase JWT токен и сохраняет сессию."""
        data = request.json
        id_token = data.get('idToken')
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
                    return jsonify({'success': True, 'redirect': url_for('parent_dashboard')})
                elif session['role'] == 'student':
                    return jsonify({'success': True, 'redirect': url_for('student_dashboard')})
                elif session['role'] == 'curator':
                    return jsonify({'success': True, 'redirect': url_for('curator_dashboard')})

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

    # ── Кабинет студента ───────────────────────────────────────────────────

    @app.route('/student')
    @login_required
    def student_dashboard():
        if session.get('role') != 'student':
            return redirect(url_for('index'))

        uid          = session['uid']
        student_data = db.reference(f'students/{uid}').get() or {}
        user_data    = db.reference(f'users/{uid}').get() or {}

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
                               pending_request=pending_request)

    # ── Кабинет куратора ───────────────────────────────────────────────────

    @app.route('/curator')
    @login_required
    def curator_dashboard():
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
                for d, present in att.items():
                    unique_dates.add(d)
                    if not present: total_misses += 1
                
                # ... existing student list logic ...
                present_cnt = sum(1 for v in att.values() if v)
                total_cnt   = len(att)
                pct         = round((present_cnt / total_cnt) * 100) if total_cnt else 0
                grade_data  = sdata.get('grade', {})
                
                # Find student parent (Optimized)
                s_parent = None
                p_id = sdata.get('parent_id')
                if p_id:
                    s_parent = db.reference(f'parents/{p_id}').get()

                students_list.append({
                    'uid': sid, 'name': sdata.get('name', '—'),
                    'email': sdata.get('email', '—'),
                    'pct': pct, 'attended': present_cnt, 'total_att': total_cnt,
                    'letter': grade_data.get('letter', '—'),
                    'gpa': grade_data.get('gpa', 0.0),
                    'parent': s_parent
                })
                all_student_data.append(sdata)

        # Average students per lesson
        avg_present = 0
        if unique_dates:
            total_present_all_time = sum(sum(1 for v in s.get('attendance', {}).values() if v) for s in all_student_data)
            avg_present = round(total_present_all_time / len(unique_dates), 1)

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

        # Risk group (attendance < 70)
        low_attendance_list = []
        for s in students_list:
            if s['pct'] < 70 and s['total_att'] > 0:
                low_attendance_list.append(s)

        today = datetime.date.today().strftime("%Y-%m-%d")
        return render_template('curator_dashboard.html',
                               curator=curator_data, user=user_data,
                               students_list=students_list, 
                               low_attendance_list=low_attendance_list,
                               today_date=today,
                               incoming_requests=incoming_requests,
                               avg_present=avg_present,
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
        room_id = request.args.get('room') # 'group' or 'sid'
        uid = session.get('uid')
        role = session.get('role')
        
        if role == 'student':
            room_path = f'chats/{uid}/group' if room_id == 'group' else f'chats/private/{uid}'
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
        room_id = data.get('room') # 'group' or 'sid'
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
            else:
                room_path = f'chats/private/{uid}'
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
        return redirect(url_for('parent_dashboard'))

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
