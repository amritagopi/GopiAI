@echo off
echo Исправление всех CSS/QSS файлов с дублирующимися селекторами...

REM Исправляем файлы тем
python fix_duplicate_selectors.py app\ui\themes

REM Исправляем файлы шрифтов
python fix_duplicate_selectors.py assets\fonts

REM Запускаем компиляцию тем после исправлений
python theme_compiler.py --compile-all --themes-dir app\ui\themes --output-dir app\ui\themes\compiled

echo Готово!
