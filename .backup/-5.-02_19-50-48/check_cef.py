import os

cef_init_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Python", "Python313", "site-packages", "cefpython3", "__init__.py")

try:
    with open(cef_init_path, 'r') as f:
        content = f.read()
        print("Содержимое файла cefpython3/__init__.py:")
        print("="*50)
        print(content)
        print("="*50)

        # Ищем поддерживаемые версии Python
        import re
        versions = re.findall(r'Python [0-9.]+', content)
        print("Найденные упоминания версий Python:")
        for v in versions:
            print(v)
except Exception as e:
    print(f"Ошибка при чтении файла: {e}")
