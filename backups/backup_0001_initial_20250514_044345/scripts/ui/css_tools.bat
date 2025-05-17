@echo off
chcp 65001 >nul
echo Утилиты CSS для GopiAI
echo =============================================

setlocal
set TOOLS_DIR=app\ui\utils\css_tools

if not exist %TOOLS_DIR% (
    echo Ошибка: Директория с утилитами CSS не найдена!
    echo Ожидаемый путь: %TOOLS_DIR%
    exit /b 1
)

echo.
echo 1. Исправить CSS/QSS файлы (устранить дублирующиеся селекторы)
echo 2. Компилировать темы
echo 3. Очистить проект от ненужных файлов
echo 4. Запустить аудит UI (simple_ui_auditor)
echo 5. Запустить аудит UI (DONT_TOUCH_MY_AUDITOR)
echo 6. Открыть директорию с утилитами
echo 7. Выход
echo.

set /p choice=Выберите действие (1-7):

if "%choice%"=="1" (
    cd %TOOLS_DIR%
    call fix_css.bat
    cd ..\..\..\..
) else if "%choice%"=="2" (
    cd %TOOLS_DIR%
    python compile_themes.py
    cd ..\..\..\..
) else if "%choice%"=="3" (
    cd %TOOLS_DIR%
    call cleanup.bat
    cd ..\..\..\..
) else if "%choice%"=="4" (
    set PYTHONIOENCODING=utf-8
    python app\ui\utils\simple_ui_auditor_final.py
) else if "%choice%"=="5" (
    set PYTHONIOENCODING=utf-8
    cd %TOOLS_DIR%
    python DONT_TOUCH_MY_AUDITOR.PY
    cd ..\..\..\..
) else if "%choice%"=="6" (
    explorer %TOOLS_DIR%
) else if "%choice%"=="7" (
    exit /b 0
) else (
    echo Неверный выбор. Пожалуйста, выберите 1-7.
    exit /b 1
)

echo.
echo =============================================
echo Готово!
echo =============================================
endlocal
