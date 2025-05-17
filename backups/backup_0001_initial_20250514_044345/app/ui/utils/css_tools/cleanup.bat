@echo off
echo Очистка проекта GopiAI от ненужных файлов
echo =============================================

setlocal
cd %~dp0

REM Запуск скрипта очистки с различными опциями
echo.
echo 1. Переместить все утилиты CSS в текущую директорию
echo 2. Удалить дублирующиеся файлы из корневой директории
echo 3. Найти и удалить временные файлы
echo 4. Полная очистка (перемещение + удаление временных файлов)
echo.

set /p choice=Выберите действие (1-4):

if "%choice%"=="1" (
    python cleanup.py --move
) else if "%choice%"=="2" (
    python cleanup.py
) else if "%choice%"=="3" (
    python cleanup.py --temp
) else if "%choice%"=="4" (
    python cleanup.py --move --temp
) else (
    echo Неверный выбор. Пожалуйста, выберите 1-4.
    exit /b 1
)

echo.
echo =============================================
echo Очистка завершена!
echo =============================================
endlocal
