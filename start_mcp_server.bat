@echo off
echo Starting GopiAI MCP Server...
echo.

REM Переходим в директорию src
cd /d "%~dp0src"

REM Проверяем наличие node_modules
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    echo.
)

REM Запускаем MCP сервер
echo Starting MCP server...
node mcp_server.js

echo.
echo MCP server stopped.
pause