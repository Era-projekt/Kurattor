@echo off
echo ==========================================
echo    КУРАТОН — Запуск платформы
echo ==========================================
echo.
echo 1. Проверка зависимостей...
pip install -r requirements.txt
echo.
echo 2. Запуск сервера...
echo После запуска ОТКРОЙТЕ в браузере: http://localhost:5000
echo.
python app.py
pause
