@echo off
REM Демонстрация использования Project Analyzer

echo Project Analyzer - Демонстрация использования
echo ===============================================
echo.

REM Переходим в директорию со скриптами
cd /d "%~dp0"

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден в PATH
    echo Убедитесь, что Python установлен и добавлен в PATH
    pause
    exit /b 1
)

REM Запускаем демонстрацию
echo Запуск демонстрации...
echo.
python demo_usage.py

echo.
echo Демонстрация завершена.
pause