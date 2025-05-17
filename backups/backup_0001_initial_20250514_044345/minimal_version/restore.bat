@echo off
echo ========================================
echo =  Восстановление полной версии GopiAI  =
echo ========================================
echo.

cd %~dp0
cd ..
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ошибка при запуске приложения!
    echo Проверьте, все ли зависимости установлены.
    echo.
    echo Для установки зависимостей выполните команду:
    echo pip install -r requirements.txt
    pause
) else (
    echo.
    echo Приложение успешно завершило работу.
)
