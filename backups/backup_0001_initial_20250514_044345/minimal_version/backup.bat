@echo off
echo ========================================
echo =    Создание резервной копии GopiAI   =
echo ========================================
echo.

set /p TAG="Введите тег резервной копии (например, 'этап1'): "
set /p DESC="Введите описание резервной копии: "

python backup_manager.py create --tag "%TAG%" --description "%DESC%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ошибка при создании резервной копии!
    pause
) else (
    echo.
    echo Резервная копия успешно создана.
    pause
)
