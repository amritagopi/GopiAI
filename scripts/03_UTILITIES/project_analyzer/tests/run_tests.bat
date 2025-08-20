@echo off
REM Запуск всех тестов для project_analyzer

echo Запуск тестов анализаторов проекта...
echo.

REM Переходим в директорию с тестами
cd /d "%~dp0"

REM Проверяем наличие pytest
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo ОШИБКА: pytest не установлен
    echo Установите pytest: pip install pytest
    pause
    exit /b 1
)

REM Запускаем тесты
echo Запуск тестов с подробным выводом...
python -m pytest . -v --tb=short

if errorlevel 1 (
    echo.
    echo ОШИБКА: Некоторые тесты не прошли
) else (
    echo.
    echo ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!
)

echo.
pause