@echo off
REM GopiAI Debug Launcher для Windows
REM Запускает приложение с детальным логированием без изменения основных файлов

echo.
echo ===============================================
echo           GopiAI Debug Mode
echo ===============================================
echo.

REM Устанавливаем переменные для детального логирования
set PYTHONUNBUFFERED=1
set PYTHONASYNCIODEBUG=1
set PYTHONVERBOSE=1
set QT_LOGGING_RULES=qt.*=true
set QT_DEBUG_PLUGINS=1
set GOPIAI_DEBUG=true

REM Генерируем имя файла логов
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,8%_%dt:~8,6%"
set "log_file=gopiai_debug_%timestamp%.log"

echo 📁 Логи сохраняются в: %log_file%
echo 🐍 Python: %PYTHON_EXE%
echo 📂 Рабочая папка: %CD%
echo.
echo 🚀 Запускаем GopiAI с детальным логированием...
echo ===============================================
echo.

REM Запускаем с перенаправлением в файл и консоль
python -u -X dev GopiAI-UI/gopiai/ui/main.py 2>&1 | tee %log_file%

echo.
echo ===============================================
echo 📁 Детальные логи сохранены в: %log_file%
echo ===============================================
pause