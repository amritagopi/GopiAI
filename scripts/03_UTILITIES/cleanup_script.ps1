# ===============================================
# СКРИПТ УБОРКИ ПРОЕКТА GOPI_AI
# Безопасное удаление файлов из списка
# ===============================================

param(
    [switch]$DryRun = $false,  # Режим "пробного запуска" - только показать что будет удалено
    [switch]$Confirm = $true   # Подтверждение перед удалением
)

Write-Host "🧹 НАЧИНАЕМ УБОРКУ ПРОЕКТА GOPI_AI" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Проверяем наличие файла списка
$deleteListFile = "C:\Users\crazy\GOPI_AI_MODULES\03_UTILITIES\files_to_delete.txt"
if (-not (Test-Path $deleteListFile)) {
    Write-Host "❌ Файл '$deleteListFile' не найден!" -ForegroundColor Red
    Write-Host "💡 Создайте файл со списком файлов для удаления" -ForegroundColor Yellow
    exit 1
}

# Читаем список файлов
Write-Host "📋 Читаем список файлов для удаления..." -ForegroundColor Yellow
$content = Get-Content $deleteListFile -Encoding UTF8
$filesToDelete = @()

foreach ($line in $content) {
    $line = $line.Trim()
    
    # Пропускаем комментарии и пустые строки
    if ($line -match '^#' -or $line -eq '') {
        continue
    }
    
    $filesToDelete += $line
}

Write-Host "📊 Найдено файлов для удаления: $($filesToDelete.Count)" -ForegroundColor Green

if ($filesToDelete.Count -eq 0) {
    Write-Host "✅ Нет файлов для удаления!" -ForegroundColor Green
    exit 0
}

# Показываем что будет удалено
Write-Host "`n📋 СПИСОК ФАЙЛОВ ДЛЯ УДАЛЕНИЯ:" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow

$existingFiles = @()
$missingFiles = @()

foreach ($file in $filesToDelete) {
    if (Test-Path $file) {
        $existingFiles += $file
        $fileInfo = Get-Item $file
        $size = if ($fileInfo.PSIsContainer) { "<DIR>" } else { "{0:N0} bytes" -f $fileInfo.Length }
        Write-Host "✅ $file ($size)" -ForegroundColor Green
    } else {
        $missingFiles += $file
        Write-Host "❌ $file (НЕ НАЙДЕН)" -ForegroundColor Red
    }
}

Write-Host "`n📊 СТАТИСТИКА:" -ForegroundColor Cyan
Write-Host "   Существующих файлов: $($existingFiles.Count)" -ForegroundColor Green
Write-Host "   Отсутствующих файлов: $($missingFiles.Count)" -ForegroundColor Red

if ($missingFiles.Count -gt 0) {
    Write-Host "`n⚠️ ВНИМАНИЕ: Некоторые файлы не найдены!" -ForegroundColor Yellow
    Write-Host "💡 Возможно, они уже удалены или путь указан неверно" -ForegroundColor Yellow
}

# Режим "пробного запуска"
if ($DryRun) {
    Write-Host "`n🔍 РЕЖИМ ПРОБНОГО ЗАПУСКА - файлы НЕ будут удалены" -ForegroundColor Magenta
    Write-Host "✅ Проверка завершена. Для реального удаления запустите без параметра -DryRun" -ForegroundColor Green
    exit 0
}

# Подтверждение удаления
if ($Confirm -and $existingFiles.Count -gt 0) {
    Write-Host "`n⚠️ ВНИМАНИЕ! Файлы будут БЕЗВОЗВРАТНО удалены!" -ForegroundColor Red
    $response = Read-Host "Продолжить удаление? (y/N)"
    
    if ($response -notmatch '^[Yy]$') {
        Write-Host "❌ Удаление отменено пользователем" -ForegroundColor Yellow
        exit 0
    }
}

# Удаляем файлы
Write-Host "`n🗑️ НАЧИНАЕМ УДАЛЕНИЕ..." -ForegroundColor Red
$deletedCount = 0
$errorCount = 0

foreach ($file in $existingFiles) {
    try {
        Write-Host "🗑️ Удаляем: $file" -ForegroundColor Yellow
        
        if (Test-Path $file -PathType Container) {
            # Это директория
            Remove-Item $file -Recurse -Force -ErrorAction Stop
        } else {
            # Это файл
            Remove-Item $file -Force -ErrorAction Stop
        }
        
        $deletedCount++
        Write-Host "   ✅ Удален" -ForegroundColor Green
    }
    catch {
        $errorCount++
        Write-Host "   ❌ Ошибка: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Удаляем пустые директории __pycache__
Write-Host "`n🧹 Проверяем пустые директории..." -ForegroundColor Yellow
$pycacheDirs = Get-ChildItem -Directory -Name "__pycache__" -Recurse -ErrorAction SilentlyContinue

foreach ($dir in $pycacheDirs) {
    try {
        $fullPath = Join-Path $PWD $dir
        if ((Get-ChildItem $fullPath -ErrorAction SilentlyContinue).Count -eq 0) {
            Write-Host "🗑️ Удаляем пустую директорию: $dir" -ForegroundColor Yellow
            Remove-Item $fullPath -ErrorAction Stop
            Write-Host "   ✅ Удалена" -ForegroundColor Green
            $deletedCount++
        }
    }
    catch {
        Write-Host "   ❌ Ошибка при удалении $dir`: $($_.Exception.Message)" -ForegroundColor Red
        $errorCount++
    }
}

# Итоговая статистика
Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "✅ УБОРКА ЗАВЕРШЕНА!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "📊 ИТОГОВАЯ СТАТИСТИКА:" -ForegroundColor Cyan
Write-Host "   Успешно удалено: $deletedCount элементов" -ForegroundColor Green
Write-Host "   Ошибок: $errorCount" -ForegroundColor $(if ($errorCount -eq 0) { "Green" } else { "Red" })
Write-Host "   Пропущено (не найдено): $($missingFiles.Count)" -ForegroundColor Yellow

if ($errorCount -eq 0) {
    Write-Host "`n🎉 Уборка прошла успешно! Проект готов к работе!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Уборка завершена с ошибками. Проверьте логи выше." -ForegroundColor Yellow
}

Write-Host "`n💝 Спасибо за аккуратность, Анютка! Проект теперь чистый и аккуратный!" -ForegroundColor Magenta
