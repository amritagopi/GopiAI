# Filesystem Tools - Файловые операции

## Основные возможности:
- **Чтение/запись файлов**: read_file(), write_file(), append_file()
- **JSON/CSV операции**: read_json(), write_json(), read_csv(), write_csv()
- **Поиск файлов**: find_files(), search_in_files()
- **Архивирование**: create_zip(), extract_zip()
- **Резервное копирование**: backup_file(), restore_backup()
- **Сравнение файлов**: compare_files(), get_file_diff()
- **Информация**: get_file_info(), get_directory_tree()
- **Хеширование**: calculate_file_hash()

## Примеры использования:

### Чтение и запись файлов:
```python
# Чтение файла
content = filesystem_tools.read_file("/path/to/file.txt")

# Запись файла
filesystem_tools.write_file("/path/to/output.txt", "Содержимое файла")

# Добавление к файлу
filesystem_tools.append_file("/path/to/log.txt", "Новая запись")
```

### Работа с JSON:
```python
# Чтение JSON
data = filesystem_tools.read_json("/path/to/data.json")

# Запись JSON
filesystem_tools.write_json("/path/to/output.json", {"key": "value"})
```

### Поиск файлов:
```python
# Поиск файлов по маске
files = filesystem_tools.find_files("/directory", "*.py")

# Поиск текста в файлах
results = filesystem_tools.search_in_files("/directory", "search_pattern")
```

### Архивирование:
```python
# Создание архива
filesystem_tools.create_zip("/path/to/archive.zip", ["/file1.txt", "/file2.txt"])

# Распаковка архива
filesystem_tools.extract_zip("/path/to/archive.zip", "/extract/to/")
```

## Важные замечания:
- Всегда используйте абсолютные пути
- Проверяйте права доступа к файлам
- При работе с большими файлами используйте потоковую обработку
- Функции чтения файлов всегда возвращают строки после декодирования