@echo off
echo Запуск GopiAI с использованием Python из виртуального окружения

:: Проверяем наличие виртуального окружения
if not exist "venv\Scripts\python.exe" (
    echo Ошибка: Виртуальное окружение не найдено в venv\Scripts\python.exe
    pause
    exit /b 1
)

:: Активируем виртуальное окружение и запускаем приложение
call venv\Scripts\activate.bat

:: Выводим версию Python
python --version

:: Запускаем приложение
python main.py %*

:: Деактивируем виртуальное окружение
call venv\Scripts\deactivate.bat

echo Приложение завершило работу
