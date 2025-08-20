@echo off
REM Project Cleanup Analyzer Batch Script
REM This script runs the project cleanup analyzer on the GopiAI project

echo ===================================================
echo GopiAI Project Cleanup Analyzer
echo ===================================================

REM Parse command-line arguments
set FORMAT=markdown
set SEVERITY=low
set DETAILED=
set SEQUENTIAL=
set CACHE=
set INCREMENTAL=
set DEPTH=standard
set MAX_FILES=

:parse_args
if "%~1"=="" goto :end_parse_args
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
if /i "%~1"=="--high-only" (
    set SEVERITY=high
    shift
    goto :parse_args
)
if /i "%~1"=="--medium-up" (
    set SEVERITY=medium
    shift
    goto :parse_args
)
if /i "%~1"=="--detailed" (
    set DETAILED=--detailed-logging
    shift
    goto :parse_args
)
if /i "%~1"=="--sequential" (
    set SEQUENTIAL=--sequential
    shift
    goto :parse_args
)
if /i "%~1"=="--no-cache" (
    set CACHE=--no-cache
    shift
    goto :parse_args
)
if /i "%~1"=="--no-incremental" (
    set INCREMENTAL=--no-incremental
    shift
    goto :parse_args
)
if /i "%~1"=="--quick" (
    set DEPTH=quick
    shift
    goto :parse_args
)
if /i "%~1"=="--full" (
    set DEPTH=full
    shift
    goto :parse_args
)
if /i "%~1"=="--max-files" (
    set MAX_FILES=--max-files %~2
    shift
    shift
    goto :parse_args
)
shift
goto :parse_args
:end_parse_args

REM Create reports directory if it doesn't exist
if not exist "..\project_health\reports" (
    mkdir "..\project_health\reports"
)

REM Activate the Python environment if available
if exist "..\gopiai_env\Scripts\activate.bat" (
    echo Activating gopiai_env environment...
    call ..\gopiai_env\Scripts\activate.bat
) else (
    echo Warning: gopiai_env not found, using system Python
)

echo.
echo Running Project Cleanup Analyzer...
echo Format: %FORMAT%
echo Severity: %SEVERITY%
echo Analysis depth: %DEPTH%
if defined DETAILED echo Detailed logging: Enabled
if defined SEQUENTIAL echo Mode: Sequential (slower but uses less memory)
if defined CACHE echo Caching: Disabled
if defined INCREMENTAL echo Incremental analysis: Disabled
if defined MAX_FILES echo %MAX_FILES%
echo.

REM Run the analyzer using the CLI script
python "%~dp0project_cleanup_cli.py" --project-path .. --format %FORMAT% --severity %SEVERITY% --depth %DEPTH% %DETAILED% %SEQUENTIAL% %CACHE% %INCREMENTAL% %MAX_FILES%

REM Check if the analysis was successful
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Analysis completed successfully.
) else (
    echo.
    echo Analysis failed with error code %ERRORLEVEL%
)

REM Deactivate the Python environment if it was activated
if exist "..\gopiai_env\Scripts\activate.bat" (
    call deactivate
)

echo.
echo Press any key to exit...
pause > nul