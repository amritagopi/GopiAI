@echo off
REM Run comprehensive test suite for Project Cleanup Analyzer

echo Running comprehensive test suite for Project Cleanup Analyzer...
echo.

REM Set up Python environment
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Run the comprehensive test suite
python test_comprehensive_suite.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo All tests passed successfully!
) else (
    echo Tests failed with error code %ERRORLEVEL%
)

pause