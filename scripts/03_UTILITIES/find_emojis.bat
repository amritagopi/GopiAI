@echo off
chcp 65001 >nul
echo 🤖 Поиск эмодзи в файлах проекта
echo =====================================

if "%1"=="" (
    echo Интерактивный режим...
    python 03_UTILITIES\emoji_finder.py
) else (
    echo Поиск в: %1
    python 03_UTILITIES\emoji_finder.py "%1"
)

pause