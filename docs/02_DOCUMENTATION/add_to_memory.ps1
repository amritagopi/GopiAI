# PowerShell Script для добавления данных в память GOPI_AI
# Кодировка: UTF-8

Set-Location "C:\Users\crazy\GOPI_AI_MODULES"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "    🧠 GOPI_AI Memory Manager - Добавление данных" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

function Show-Menu {
    Write-Host "Выберите способ добавления данных:" -ForegroundColor White
    Write-Host ""
    Write-Host "[1] Ввести текст вручную" -ForegroundColor Green
    Write-Host "[2] Загрузить из файла (txt/md)" -ForegroundColor Green  
    Write-Host "[3] Выход" -ForegroundColor Red
    Write-Host ""
}

function Add-ManualText {
    Write-Host ""
    Write-Host "─────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "📝 Ручной ввод данных" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host ""
    
    $sessionName = Read-Host "Название сессии памяти"
    Write-Host ""
    Write-Host "Введите ваш текст (пустая строка завершает ввод):" -ForegroundColor Cyan
    
    $textLines = @()
    $lineNumber = 1
    
    do {
        $line = Read-Host "[$lineNumber]"
        if ($line -ne "") {
            $textLines += $line
            $lineNumber++
        }
    } while ($line -ne "")
    
    $textContent = $textLines -join "`n"
    
    if ($textContent.Length -gt 0) {
        Write-Host ""
        Write-Host "🔄 Добавляем данные в память..." -ForegroundColor Yellow
        
        # Создаем временный Python скрипт
        $pythonScript = @"
from rag_memory_system.simple_memory_manager import get_memory_manager
import sys

try:
    manager = get_memory_manager()
    session = manager.create_session('$sessionName')
    content = '''$textContent'''
    manager.add_message(session, 'assistant', content)
    print('✅ Данные успешно добавлены в память!')
    print('📁 Сессия: $sessionName')
    print('📊 Добавлено строк: $($textLines.Count)')
except Exception as e:
    print('❌ Ошибка:', str(e))
"@
        
        $pythonScript | Out-File -FilePath "temp_memory.py" -Encoding UTF8
        python temp_memory.py
        Remove-Item "temp_memory.py" -ErrorAction SilentlyContinue
    } else {
        Write-Host "❌ Текст не введен!" -ForegroundColor Red
    }
}

function Add-FileContent {
    Write-Host ""
    Write-Host "─────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "📁 Загрузка из файла" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host ""
    
    $filePath = Read-Host "Путь к файлу (txt/md)"
    
    if (-not (Test-Path $filePath)) {
        Write-Host "❌ Файл не найден: $filePath" -ForegroundColor Red
        return
    }
    
    $sessionName = Read-Host "Название сессии памяти"
    Write-Host ""
    Write-Host "🔄 Читаем файл и добавляем в память..." -ForegroundColor Yellow
    
    try {
        $content = Get-Content $filePath -Raw -Encoding UTF8
        $fileName = Split-Path $filePath -Leaf
        
        # Создаем временный Python скрипт
        $pythonScript = @"
from rag_memory_system.simple_memory_manager import get_memory_manager
import os

try:
    manager = get_memory_manager()
    session = manager.create_session('$sessionName')
    
    file_info = '''Файл: $fileName
Путь: $filePath

$content'''
    
    manager.add_message(session, 'assistant', file_info)
    
    print('✅ Файл успешно добавлен в память!')
    print('📁 Сессия: $sessionName')
    print('📄 Файл: $fileName')
    print('📊 Размер: $($content.Length) символов')
    
except Exception as e:
    print('❌ Ошибка:', str(e))
"@
        
        $pythonScript | Out-File -FilePath "temp_memory.py" -Encoding UTF8
        python temp_memory.py
        Remove-Item "temp_memory.py" -ErrorAction SilentlyContinue
        
    } catch {
        Write-Host "❌ Ошибка чтения файла: $_" -ForegroundColor Red
    }
}

# Основной цикл
do {
    Show-Menu
    $choice = Read-Host "Ваш выбор (1-3)"
    
    switch ($choice) {
        "1" { Add-ManualText }
        "2" { Add-FileContent }
        "3" { 
            Write-Host ""
            Write-Host "👋 До свидания!" -ForegroundColor Green
            break 
        }
        default { 
            Write-Host "❌ Неверный выбор! Попробуйте снова." -ForegroundColor Red 
        }
    }
    
    if ($choice -ne "3") {
        Write-Host ""
        Read-Host "Нажмите Enter для продолжения"
        Clear-Host
    }
    
} while ($choice -ne "3")
