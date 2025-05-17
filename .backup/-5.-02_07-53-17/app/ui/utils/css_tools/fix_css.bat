@echo off
echo Комплексное исправление CSS/QSS файлов GopiAI
echo =============================================

setlocal
cd %~dp0
set ROOT_DIR=..\..\..\..

REM Сначала наш новый скрипт css_fixer.py
echo Запуск css_fixer.py для тем...
python css_fixer.py %ROOT_DIR%\app\ui\themes

echo Запуск css_fixer.py для шрифтов...
python css_fixer.py %ROOT_DIR%\assets\fonts

REM Затем запускаем исходный css_refactor.py
echo Запуск css_refactor.py для тем...
python css_refactor.py %ROOT_DIR%\app\ui\themes\DARK-theme.qss --fix-duplicates
python css_refactor.py %ROOT_DIR%\app\ui\themes\LIGHT-theme.qss --fix-duplicates

echo Запуск css_refactor.py для шрифтов...
python css_refactor.py %ROOT_DIR%\assets\fonts\fonts.css --fix-duplicates
python css_refactor.py %ROOT_DIR%\assets\fonts\fonts-fixed.css --fix-duplicates

REM Финальное исправление по вариациям селекторов
echo Финальная проверка дублирующихся селекторов...
python fix_duplicate_selectors.py %ROOT_DIR%\app\ui\themes

echo Компиляция тем...
python compile_themes.py

echo Готово!
echo =============================================
echo Все CSS/QSS файлы были обработаны.
echo Утилиты css_tools в app\ui\utils\css_tools
echo =============================================
endlocal
