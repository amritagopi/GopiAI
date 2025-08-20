@echo off
title Full Project Analyzer
set "UTIL_DIR=C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES"
cd /d "%UTIL_DIR%"

echo Starting Quick Analysis...
python project_analyzer\runners\quick_analyze.py --skip-duplicate --max-files 50 --format markdown
echo Quick Analysis completed!

echo Starting Strict Analysis...
python project_analyzer\runners\strict_analyzer.py --skip-duplicate --timeout 300 --format markdown
echo Strict Analysis completed!

echo Starting Full Analysis...
python analyze_project.py
echo Full Analysis completed!

echo All analyses finished! Check project_health/reports/ for results.
pause 