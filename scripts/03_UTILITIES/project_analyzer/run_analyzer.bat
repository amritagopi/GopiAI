@echo off
chcp 65001 > nul
REM Project Analyzer - Главное меню
REM Этот скрипт предоставляет удобный доступ ко всем функциям анализатора

title Project Analyzer - Главное меню

:MAIN_MENU
cls
echo.
echo ===============================================
echo           PROJECT ANALYZER v1.0
echo ===============================================
echo.
echo Выберите тип анализа:
echo.
echo 1. Быстрый анализ (рекомендуется)
echo 2. Строгий анализ (только файлы проекта)
echo 3. Полный анализ (детальный)
echo 4. Демонстрация возможностей
echo 5. Запуск тестов
echo 6. Справка
echo 0. Выход
echo.
set /p choice="Введите номер (0-6): "

if "%choice%"=="1" goto QUICK_ANALYSIS
if "%choice%"=="2" goto STRICT_ANALYSIS
if "%choice%"=="3" goto FULL_ANALYSIS
if "%choice%"=="4" goto DEMO
if "%choice%"=="5" goto TESTS
if "%choice%"=="6" goto HELP
if "%choice%"=="0" goto EXIT
goto INVALID_CHOICE

:QUICK_ANALYSIS
cls
echo ===============================================
echo              БЫСТРЫЙ АНАЛИЗ
echo ===============================================
echo.
echo Параметры:
echo - Ограничение файлов: 50
echo - Пропуск дубликатов: Да
echo - Формат отчета: HTML
echo.
echo Запуск анализа...
cd /d "%~dp0\runners"
call quick_analyze.bat --max-files 50 --skip-duplicate --format html
echo.
echo Анализ завершен!
pause
goto MAIN_MENU

:STRICT_ANALYSIS
cls
echo ===============================================
echo              СТРОГИЙ АНАЛИЗ
echo ===============================================
echo.
echo Параметры:
echo - Только файлы проекта
echo - Исключение системных папок
echo - Таймаут: 5 минут
echo.
echo Запуск анализа...
cd /d "%~dp0\runners"
call strict_analyze.bat --timeout 300 --skip-duplicate
echo.
echo Анализ завершен!
pause
goto MAIN_MENU

:FULL_ANALYSIS
cls
echo ===============================================
echo              ПОЛНЫЙ АНАЛИЗ
echo ===============================================
echo.
echo ВНИМАНИЕ: Полный анализ может занять 10-30 минут!
echo.
set /p confirm="Продолжить? (y/n): "
if /i not "%confirm%"=="y" goto MAIN_MENU

echo.
echo Запуск полного анализа...
cd /d "%~dp0\runners"
call analyze_gopi_project.bat
echo.
echo Анализ завершен!
pause
goto MAIN_MENU

:DEMO
cls
echo ===============================================
echo           ДЕМОНСТРАЦИЯ ВОЗМОЖНОСТЕЙ
echo ===============================================
echo.
cd /d "%~dp0\runners"
call demo_usage.bat
pause
goto MAIN_MENU

:TESTS
cls
echo ===============================================
echo               ЗАПУСК ТЕСТОВ
echo ===============================================
echo.
cd /d "%~dp0\tests"
call run_tests.bat
pause
goto MAIN_MENU

:HELP
cls
echo ===============================================
echo                  СПРАВКА
echo ===============================================
echo.
echo ТИПЫ АНАЛИЗА:
echo.
echo 1. БЫСТРЫЙ АНАЛИЗ
echo    - Время выполнения: 1-3 минуты
echo    - Ограниченное количество файлов
echo    - Подходит для регулярных проверок
echo.
echo 2. СТРОГИЙ АНАЛИЗ  
echo    - Время выполнения: 3-5 минут
echo    - Только файлы проекта
echo    - Безопасный для CI/CD
echo.
echo 3. ПОЛНЫЙ АНАЛИЗ
echo    - Время выполнения: 10-30 минут
echo    - Максимальная детализация
echo    - Все анализаторы включены
echo.
echo РЕЗУЛЬТАТЫ:
echo Все отчеты сохраняются в папке:
echo project_health\reports\
echo.
echo ДОКУМЕНТАЦИЯ:
echo - README.md - Полная документация
echo - QUICK_START.md - Быстрый старт
echo - MIGRATION.md - Руководство по миграции
echo.
pause
goto MAIN_MENU

:INVALID_CHOICE
cls
echo.
echo ОШИБКА: Неверный выбор!
echo Пожалуйста, введите число от 0 до 6.
echo.
pause
goto MAIN_MENU

:EXIT
echo.
echo Спасибо за использование Project Analyzer!
echo.
exit /b 0