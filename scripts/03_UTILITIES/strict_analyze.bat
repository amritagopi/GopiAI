@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════
echo     🔒 GopiAI Strict Project Analyzer
echo ═══════════════════════════════════════════════════════
echo.

REM Проверяем, что мы находимся в правильной директории
if not exist "project_cleanup_cli.py" (
    echo ❌ Ошибка: Запустите этот скрипт из директории 03_UTILITIES
    echo.
    pause
    exit /b 1
)

REM Активируем окружение Python, если оно доступно
if exist "..\gopiai_env\Scripts\activate.bat" (
    echo 🔄 Активация окружения gopiai_env...
    call ..\gopiai_env\Scripts\activate.bat
) else (
    echo ℹ️ Окружение gopiai_env не найдено, используем системный Python
)

echo.
echo 🔍 Запуск строго ограниченного анализа проекта GopiAI...
echo ⚠️ Анализ будет ограничен ТОЛЬКО директорией проекта GOPI_AI_MODULES
echo.

REM Парсим аргументы командной строки
set SKIP_DUPLICATE=
set SKIP_CONFLICT=
set MAX_FILES=100
set TIMEOUT=300
set FORMAT=markdown

:parse_args
if "%~1"=="" goto :end_parse_args
if /i "%~1"=="--skip-duplicate" (
    set SKIP_DUPLICATE=--skip-duplicate
    shift
    goto :parse_args
)
if /i "%~1"=="--skip-conflict" (
    set SKIP_CONFLICT=--skip-conflict
    shift
    goto :parse_args
)
if /i "%~1"=="--max-files" (
    set MAX_FILES=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--timeout" (
    set TIMEOUT=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--format" (
    set FORMAT=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--html" (
    set FORMAT=html
    shift
    goto :parse_args
)
if /i "%~1"=="--json" (
    set FORMAT=json
    shift
    goto :parse_args
)
shift
goto :parse_args
:end_parse_args

echo Настройки анализа:
echo - Формат отчета: %FORMAT%
echo - Максимум файлов: %MAX_FILES%
echo - Таймаут: %TIMEOUT% секунд
if defined SKIP_DUPLICATE echo - Пропуск анализа дублирующегося кода: Да
if defined SKIP_CONFLICT echo - Пропуск анализа конфликтов: Да
echo.

REM Запускаем скрипт анализа
python strict_analyzer.py %SKIP_DUPLICATE% %SKIP_CONFLICT% --max-files %MAX_FILES% --timeout %TIMEOUT% --format %FORMAT%

REM Проверяем результат выполнения
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Анализ успешно завершен!
) else (
    echo.
    echo ❌ Анализ завершился с ошибкой (код %ERRORLEVEL%)
)

REM Деактивируем окружение, если оно было активировано
if exist "..\gopiai_env\Scripts\activate.bat" (
    call deactivate
)

echo.
echo Нажмите любую клавишу для выхода...
pause > nul