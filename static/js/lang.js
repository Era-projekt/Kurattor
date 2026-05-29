/* =========================================================
   KURATON — Мультиязычность (RU / KK)
   ========================================================= */
const translations = {
    ru: {
        // Navbar
        nav_home:         "Главная",
        nav_search:       "Поиск",
        nav_dashboard:    "Кабинет",
        nav_login:        "Войти",
        nav_logout:       "Выйти",

        // Hero / Index
        hero_badge:       "Платформа нового поколения",
        hero_title_1:     "Будущее",
        hero_title_2:     "образования",
        hero_title_3:     "уже здесь.",
        hero_desc:        "Присоединяйтесь к Kuraton. Найдите идеального наставника, отслеживайте посещаемость и оценивайте успехи — всё в одном месте.",
        hero_btn_start:   "Начать работу →",
        hero_btn_search:  "Найти куратора",
        hero_btn_cabinet: "В мой кабинет →",
        stat_students:    "Студентов",
        stat_curators:    "Кураторов",
        stat_profs:       "Специальностей",
        features_title:   "Почему выбирают Kuraton?",
        features_sub:     "Всё что нужно студенту и куратору — в одном продуманном интерфейсе.",
        features_f1_title: "Smart-выбор куратора",
        features_f1_desc:  "Система автоматически предложит кураторов по вашей специальности.",
        features_f2_title: "Аналитика в реальном времени",
        features_f2_desc:  "Диаграммы посещаемости и успеваемости обновляются сразу.",
        features_f3_title: "AI Помощник 24/7",
        features_f3_desc:  "Встроенный чат-бот на базе Gemini API отвечает на ваши вопросы.",

        // Auth
        auth_login_title:    "Добро пожаловать",
        auth_register_title: "Создать аккаунт",
        auth_no_account:     "Нет аккаунта?",
        auth_has_account:    "Уже есть аккаунт?",
        auth_login_link:     "Войти",
        auth_register_link:  "Зарегистрироваться",
        auth_name:           "ФИО",
        auth_role:           "Роль",
        auth_profession:     "Специальность",
        auth_password:       "Пароль",
        auth_btn_login:      "Войти в аккаунт",
        auth_btn_register:   "Зарегистрироваться",
        role_student:        "Студент",
        role_curator:        "Куратор",
        role_student_desc:   "Выбрать куратора",
        role_curator_desc:   "Управлять группой",
        auth_quote:          "Знания — это твой путь к успеху.",
        auth_quote_sub:      "Платформа для студентов и кураторов казахстанских университетов",
        auth_testimonial:    "Kuraton сделал процесс поиска куратора простым и быстрым. Нашел наставника за 2 минуты!",
        auth_testimonial_name: "Абылай К.",
        auth_testimonial_role: "Студент, IT — 2 курс",

        // Professions
        prof_it:       "💻 IT (Информационные технологии)",
        prof_econ:     "📈 Экономика",
        prof_med:      "🏥 Медицина",
        prof_law:      "⚖️ Юриспруденция",
        prof_design:   "🎨 Дизайн",

        std_title:       "Мой кабинет",
        std_curator:     "Мой куратор",
        std_no_curator:  "Не назначен",
        std_no_curator_msg: "У вас пока нет куратора",
        std_choose_cur:  "Выбрать куратора",
        std_available:   "Доступные кураторы:",
        std_no_avail:    "Нет доступных кураторов (лимит 20 студентов исчерпан)",
        std_choose_btn:  "Выбрать",
        std_curator_hint: "Ваш куратор закреплён. Обратитесь по вопросам учёбы.",
        std_attendance_title: "Посещаемость",
        std_current_semester: "Текущий семестр",
        std_visits:      "посещений",
        std_attended_label: "Посещено",
        std_missed_label: "Пропущено",
        std_grade_label: "Итоговая оценка",
        std_att_table_title: "История посещаемости",
        std_loading:     "Загрузка...",
        stat_attended:   "Посещено",
        stat_lessons:    " занятий",
        stat_grade:      "Успеваемость",
        stat_semester:   "Семестр",
        btn_issue_grade: "Выдать оценку",
        th_date:         "Дата",
        th_status:       "Статус",

        // Curator Dashboard
        cur_title:         "Кабинет куратора",
        cur_my_group:      "Моя группа",
        cur_students:      "Студентов",
        cur_mark_att:      "Отметить посещаемость",
        cur_mark_att_desc: "Выберите дату и отметьте присутствующих студентов",
        cur_student_list:  "Список студентов",
        cur_no_students:   "В группе пока нет студентов",
        cur_no_students_desc: "Студенты появятся здесь, как только выберут вас куратором",
        cur_persons:       "чел.",
        cur_avg_attendance: "Средняя явка",
        cur_risk_group:    "В группе риска",
        cur_semester:      "Семестр",
        cur_new_requests:  "Новые запросы",
        cur_requests_desc: "Студенты хотят присоединиться к вашей группе",
        btn_save:          "Сохранить",
        btn_issue_all:     "Выдать всем",
        btn_export:        "Экспорт",
        btn_new_semester:  "Новый семестр",
        btn_approve:       "Принять",
        btn_reject:        "Отклонить",
        att_present:       "✓ Присутствует",
        att_absent:        "✗ Отсутствует",

        // Tabs
        tab_students:      "Студенты",
        tab_schedule:      "Расписание",
        tab_library:       "Библиотека",
        tab_chat:          "Чат и Связь",

        // Schedule
        sched_mon: "Пн", sched_tue: "Вт", sched_wed: "Ср", sched_thu: "Чт", sched_fri: "Пт", sched_sat: "Сб",
        sched_time: "Время",
        sched_room: "Аудитория",
        sched_add_subject: "Введите предмет:", sched_delete_confirm: "Удалить предмет?",

        // Library
        lib_materials: "Учебные материалы",
        lib_upload_btn: "Загрузить файл",
        lib_open_btn: "Открыть файл",
        lib_type_pdf: "Документ PDF", lib_type_ppt: "Презентация", lib_type_vid: "Видеолекция", lib_type_doc: "Методичка",
        lib_delete_confirm: "Вы уверены, что хотите удалить этот материал?",
        lib_upload_select: "Выберите файл:", lib_upload_name: "Название:", lib_upload_submit: "Загрузить в библиотеку",

        // Chat
        chat_title_group: "Групповой чат",
        chat_warning: "Предупреждение",
        chat_placeholder: "Введите сообщение...",
        chat_send: "Отправить",

        // Table headers
        th_student:    "Студент",
        table_attendance: 'Посещаемость',
        table_letter: 'Оценка',
        table_actions: 'Действие',
        th_today:      "Сегодня",
        th_actions:    "Действия",

        // Labels
        label_profession: "Специальность:",
        label_semester:   "Семестр",
        stat_attendance:  "Ср. посещаемость",
        stat_avg_grade:   "Ср. GPA",
        hero_pill_stats:  "Аналитика",

        // Search
        search_title: "Поиск пользователей",
        search_sub:   "Найдите студентов и кураторов по имени или специальности",
        search_placeholder: "Введите имя, специальность...",
        nav_search_students: "Поиск студентов",
        search_filter_all: "Все",
        search_start_typing: "Начните вводить текст",
        search_hint: "Поиск выполняется по имени и специальности",
        search_results_found: "Найдено",
        search_no_results: "Ничего не найдено",

        // Chatbot
        chatbot_title:    "AI Помощник",
        chatbot_greeting: "Сәлем! Мен Kuraton AI-помощникімін. Чем могу помочь?",
        chatbot_placeholder: "Введите сообщение...",
        footer_text:      "© 2026 Kuraton. Все права защищены.",

        // Extra Dashboard Translations
        std_misses_count: "Пропусков",
        std_visited_lessons: "Посещено занятий",
        std_total_lessons: "Всего занятий",
        std_your_curator: "Ваш куратор",
        std_curator_chat: "Чат с куратором",
        std_parent_connection: "Родительская связь",
        std_parent_active: "Общий доступ активен",
        std_parent_not_linked: "Родитель не привязан",
        nav_dashboard_title: "Мой профиль",
        chat_rooms: "Комнаты",
        chat_personal: "Личные чаты",
        th_parent: "Родитель",
        chat_contacts: "Контакты",
        chat_all_flow: "Весь поток",
        notif_title: "Уведомления",
        notif_empty: "Новых уведомлений нет",
    },

    kk: {
        // Navbar
        nav_home:      "Басты бет",
        nav_search:    "Іздеу",
        nav_dashboard: "Кабинет",
        nav_login:     "Кіру",
        nav_logout:    "Шығу",

        // Hero / Index
        hero_badge:    "Жаңа ұрпақ платформасы",
        hero_title_1:  "Білімнің",
        hero_title_2:  "болашағы",
        hero_title_3:  "осында.",
        hero_desc:     "Kuraton платформасына қосылыңыз. Тəлімгеріңізді табыңыз, сабаққа қатысуды бақылаңыз жəне жетістіктеріңізді бағалаңыз.",
        hero_btn_start:   "Бастау →",
        hero_btn_search:  "Куратор табу",
        hero_btn_cabinet: "Кабинетке →",
        stat_students:    "Студент",
        stat_curators:    "Куратор",
        stat_profs:       "Мамандық",
        features_title:   "Неліктен Kuraton таңдайды?",
        features_sub:     "Студент пен кураторға қажеттінің бәрі — бір жерде.",
        features_f1_title: "Smart-куратор таңдау",
        features_f1_desc:  "Жүйе сіздің мамандығыңыз бойынша кураторларды автоматты түрде ұсынады.",
        features_f2_title: "Нақты уақытта аналитика",
        features_f2_desc:  "Қатысу жəне үлгерім диаграммалары бірден жаңартылады.",
        features_f3_title: "AI Көмекші 24/7",
        features_f3_desc:  "Gemini API негізіндегі чат-бот сұрақтарыңызға жауап береді.",

        // Auth
        auth_login_title:    "Қош келдіңіз",
        auth_register_title: "Тіркелу",
        auth_no_account:     "Аккаунтыңыз жоқ па?",
        auth_has_account:    "Аккаунтыңыз бар ма?",
        auth_login_link:     "Кіру",
        auth_register_link:  "Тіркелу",
        auth_name:           "Аты-жөні",
        auth_role:           "Рөл",
        auth_profession:     "Мамандық",
        auth_password:       "Құпия сөз",
        auth_btn_login:      "Жүйеге кіру",
        auth_btn_register:   "Тіркелу",
        role_student:        "Студент",
        role_curator:        "Куратор",
        role_student_desc:   "Куратор таңдау",
        role_curator_desc:   "Топты басқару",
        auth_quote:          "Білім — бұл сенің табысқа барар жолың.",
        auth_quote_sub:      "Қазақстандық университеттердің студенттері мен кураторларына арналған платформа",
        auth_testimonial:    "Kuraton куратор іздеу процесін жеңіл әрі жылдам етті. 2 минутта тәлімгер таптым!",
        auth_testimonial_name: "Абылай К.",
        auth_testimonial_role: "Студент, IT — 2 курс",

        // Professions
        prof_it:     "💻 IT (Ақпараттық технологиялар)",
        prof_econ:   "📈 Экономика",
        prof_med:    "🏥 Медицина",
        prof_law:    "⚖️ Құқықтану",
        prof_design: "🎨 Дизайн",

        // Student Dashboard
        std_title:       "Менің кабинетім",
        std_curator:     "Менің кураторым",
        std_no_curator:  "Тағайындалмаған",
        std_no_curator_msg: "Кураторыңыз əлі жоқ",
        std_choose_cur:  "Куратор таңдау",
        std_available:   "Қолжетімді кураторлар:",
        std_no_avail:    "Қолжетімді куратор жоқ (20 студент лимиті толды)",
        std_choose_btn:  "Таңдау",
        std_curator_hint: "Кураторыңыз бекітілген. Оқу мəселелері бойынша хабарласыңыз.",
        std_attendance_title: "Сабаққа қатысу",
        std_current_semester: "Ағымдағы семестр",
        std_visits:      "қатысу",
        std_attended_label: "Қатысты",
        std_missed_label: "Қатыспады",
        std_grade_label: "Қорытынды баға",
        std_att_table_title: "Қатысу тарихы",
        std_loading:     "Жүктелуде...",
        stat_attended:   "Қатысты",
        stat_lessons:    " сабақ",
        stat_grade:      "Үлгерім",
        stat_semester:   "Семестр 1",
        btn_issue_grade: "Баға жазу",
        th_date:         "Күні",
        th_status:       "Мəртебе",

        // Curator Dashboard
        cur_title:         "Куратор кабинеті",
        cur_my_group:      "Менің тобым",
        cur_students:      "Студент",
        cur_mark_att:      "Қатысуды белгілеу",
        cur_mark_att_desc: "Күнді таңдап, қатысқан студенттерді белгілеңіз",
        cur_student_list:  "Студенттер тізімі",
        cur_no_students:   "Топта əзірге студент жоқ",
        cur_no_students_desc: "Студенттер сізді куратор ретінде таңдаған кезде пайда болады",
        cur_persons:       "адам",
        btn_save:          "Сақтау",
        btn_issue_all:     "Барлығына жазу",
        btn_export:        "Экспорт",
        btn_new_semester:  "Жаңа семестр",
        att_present:       "✓ Қатысты",
        att_absent:        "✗ Қатыспады",
        
        // Tabs
        tab_students:      "Студенттер",
        tab_schedule:      "Сабақ кестесі",
        tab_library:       "Кітапхана",
        tab_chat:          "Чат және хабарламалар",
        
        // Library
        lib_materials: "Оқу материалдары",
        lib_upload_btn: "Файлды жүктеу",
        lib_open_btn: "Файлды ашу",
        lib_type_pdf: "PDF құжаты", lib_type_ppt: "Презентация", lib_type_vid: "Бейне дәріс", lib_type_doc: "Әдістемелік құрал",
        lib_delete_confirm: "Бұл материалды жойғыңыз келетініне сенімдісіз бе?",
        lib_upload_select: "Файлды таңдаңыз:", lib_upload_name: "Атауы:", lib_upload_submit: "Кітапханаға жүктеу",

        // Table headers
        th_student:    "Студент",
        th_attendance: "Қатысу",
        th_grade:      "Баға",
        th_gpa:        "GPA",
        th_today:      "Бүгін",
        th_actions:    "Əрекет",

        // Labels
        label_profession: "Мамандық:",
        label_semester:   "Семестр",
        stat_attendance:  "Орт. қатысу",
        stat_avg_grade:   "Орт. GPA",

        // Search
        search_title: "Пайдаланушыларды іздеу",
        search_sub:   "Студент жəне кураторларды аты немесе мамандығы бойынша табыңыз",
        search_placeholder: "Аты, мамандық...",
        nav_search_students: "Студенттерді іздеу",
        search_filter_all: "Барлығы",
        search_start_typing: "Мәтінді енгізе бастаңыз",
        search_hint: "Іздеу аты және мамандығы бойынша жүргізіледі",
        search_results_found: "Табылды",
        search_no_results: "Ештеңе табылмады",

        // Chatbot
        chatbot_title:       "AI Көмекші",
        chatbot_greeting:    "Сəлем! Мен Kuraton AI-көмекшісімін. Қандай сұрақ бар?",
        chatbot_placeholder: "Хабарлама жазыңыз...",
        footer_text:         "© 2026 Kuraton. Барлық құқықтар қорғалған.",

        // Extra Dashboard Translations
        std_misses_count: "Қатыспағандар саны",
        std_visited_lessons: "Қатысқан сабақтар",
        std_total_lessons: "Барлық сабақтар",
        std_your_curator: "Сіздің кураторыңыз",
        std_curator_chat: "Куратормен чат",
        std_parent_connection: "Ата-анамен байланыс",
        std_parent_active: "Ортақ рұқсат белсенді",
        std_parent_not_linked: "Ата-ана байланыспаған",
        nav_dashboard_title: "Менің профилім",
        chat_rooms: "Бөлмелер",
        chat_personal: "Жеке чаттар",
        th_parent: "Ата-ана",
        chat_contacts: "Байланыстар",
        chat_all_flow: "Барлық ағын",
        notif_title: "Хабарламалар",
        notif_empty: "Жаңа хабарламалар жоқ",
    }
};

/* =========================================================
   ENGINE
   ========================================================= */
document.addEventListener("DOMContentLoaded", () => {
    const switcher = document.getElementById("lang-switcher");
    let lang = localStorage.getItem("kuraton_lang") || "ru";
    if (switcher) switcher.value = lang;

    window.applyTranslations = () => {
        // Text content
        document.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            if (translations[lang]?.[key] !== undefined) el.innerText = translations[lang][key];
        });
        // Placeholders
        document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
            const key = el.getAttribute("data-i18n-placeholder");
            if (translations[lang]?.[key]) el.setAttribute("placeholder", translations[lang][key]);
        });
    };

    if (switcher) {
        switcher.addEventListener("change", e => {
            lang = e.target.value;
            localStorage.setItem("kuraton_lang", lang);
            window.applyTranslations();
            if (typeof loadLibrary === "function") {
                loadLibrary();
            }
        });
    }

    window.applyTranslations();
});
