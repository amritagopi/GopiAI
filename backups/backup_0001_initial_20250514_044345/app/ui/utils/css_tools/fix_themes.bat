@echo off
echo Fixing themes and creating color variables for GopiAI

REM Create color variables directory if not exists
mkdir app\ui\themes\vars 2>nul

REM Fix duplicates in DARK theme
echo Fixing duplicates in DARK theme...
python css_refactor.py app\ui\themes\DARK-theme.qss --fix-duplicates --output app\ui\themes\DARK-theme-fixed.qss

REM Fix duplicates in LIGHT theme
echo Fixing duplicates in LIGHT theme...
python css_refactor.py app\ui\themes\LIGHT-theme.qss --fix-duplicates --output app\ui\themes\LIGHT-theme-fixed.qss

REM Extract colors from DARK theme
echo Extracting colors from DARK theme...
python css_refactor.py app\ui\themes\DARK-theme-fixed.qss --fix-colors --vars app\ui\themes\vars\dark-colors.qss

REM Extract colors from LIGHT theme
echo Extracting colors from LIGHT theme...
python css_refactor.py app\ui\themes\LIGHT-theme-fixed.qss --fix-colors --vars app\ui\themes\vars\light-colors.qss

REM Fix fonts.css
echo Fixing fonts.css...
python fonts_fixer.py assets\fonts\fonts.css assets\fonts\fonts-fixed.css

REM Compile themes with new variables
echo Compiling themes with color variables...
python theme_compiler.py --generate-vars --themes-dir app\ui\themes --output-dir app\ui\themes\vars
python theme_compiler.py --compile-all --themes-dir app\ui\themes --output-dir app\ui\themes\compiled

echo Done!
echo.
echo Fixed files:
echo - app\ui\themes\DARK-theme-fixed.qss
echo - app\ui\themes\LIGHT-theme-fixed.qss
echo - assets\fonts\fonts-fixed.css
echo.
echo Created color variables:
echo - app\ui\themes\vars\dark-colors.qss
echo - app\ui\themes\vars\light-colors.qss
echo.
echo Compiled themes:
echo - app\ui\themes\compiled\dark-theme.qss
echo - app\ui\themes\compiled\light-theme.qss
echo.
