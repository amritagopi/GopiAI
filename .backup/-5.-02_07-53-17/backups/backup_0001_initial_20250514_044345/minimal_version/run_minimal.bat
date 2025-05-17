@echo off
echo ========================================
echo =   Запуск минимальной версии GopiAI   =
echo ========================================
echo.

cd %~dp0
python minimal_app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ошибка при запуске приложения!
    echo Проверьте, установлен ли Python и PySide6.
    echo.
    echo Для установки PySide6 выполните команду:
    echo pip install PySide6
    pause
) else (
    echo.
    echo Приложение успешно завершило работу.
)
