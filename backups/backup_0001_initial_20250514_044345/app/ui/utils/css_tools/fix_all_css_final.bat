@echo off
echo Комплексное исправление всех CSS/QSS файлов

REM Сначала наш новый скрипт
echo Запуск css_fixer.py для тем...
python css_fixer.py app\ui\themes

echo Запуск css_fixer.py для шрифтов...
python css_fixer.py assets\fonts

REM Затем запускаем исходный css_refactor.py для полного исправления
echo Запуск css_refactor.py для тем...
python css_refactor.py app\ui\themes\DARK-theme.qss --fix-duplicates
python css_refactor.py app\ui\themes\LIGHT-theme.qss --fix-duplicates

echo Запуск css_refactor.py для шрифтов...
python css_refactor.py assets\fonts\fonts.css --fix-duplicates
python css_refactor.py assets\fonts\fonts-fixed.css --fix-duplicates

REM Финальное исправление по вариациям селекторов
echo Финальная проверка дублирующихся селекторов...
python fix_duplicate_selectors.py app\ui\themes

echo Компиляция тем...
python compile_themes.py

echo Готово!
echo =============================================
echo Все CSS/QSS файлы были обработаны следующими скриптами:
echo 1. css_fixer.py - исправление дублирующихся селекторов
echo 2. css_refactor.py - дополнительное исправление дубликатов
echo 3. fix_duplicate_selectors.py - исправление вариаций селекторов
echo 4. compile_themes.py - компиляция и исправление путей в темах
echo =============================================
