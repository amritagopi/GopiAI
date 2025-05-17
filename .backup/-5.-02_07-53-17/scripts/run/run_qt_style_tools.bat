@echo off
chcp 65001 >nul
REM Скрипт для запуска инструментов стилизации Qt

echo =========================================
echo Средства стилизации интерфейса Qt
echo =========================================
echo.

REM Убедимся, что Python доступен
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Ошибка: Python не найден. Пожалуйста, установите Python и добавьте его в PATH.
    exit /b 1
)

echo Проверка и установка необходимых пакетов...
python -m pip install PyQt5 PySide6 QStyler qt-style-sheet-inspector

echo.
echo Выберите инструмент для запуска:
echo 1 - QStyler (редактор и тестировщик стилей на PyQt5)
echo 2 - Qt Style Sheet Inspector (инспектор стилей в реальном времени)
echo 3 - Демонстрация стилей (с использованием PySide6)
echo.

set /p choice=Ваш выбор (1/2/3):

if "%choice%"=="1" (
    echo Запуск QStyler...
    python -m QStyler
) else if "%choice%"=="2" (
    echo Запуск Qt Style Sheet Inspector...
    python run_style_inspector.py
) else if "%choice%"=="3" (
    echo Запуск демонстрации стилей...
    python run_style_inspector.py
) else (
    echo Неверный выбор. Пожалуйста, введите 1, 2 или 3.
    exit /b 1
)

echo.
echo Готово!
pause
