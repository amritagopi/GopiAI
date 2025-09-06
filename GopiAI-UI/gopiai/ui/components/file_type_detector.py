"""
File Type Detector для системы иконок файлов
==========================================

Система определения типов файлов и соответствующих иконок.
"""

import os


class FileTypeDetector:
    """Определитель типов файлов и их иконок"""
    
    # Маппинг расширений к типам файлов и иконкам
    FILE_TYPE_MAPPING = {
        # Изображения
        '.png': ('image', 'image'),
        '.jpg': ('image', 'image'),
        '.jpeg': ('image', 'image'),
        '.gif': ('image', 'image'),
        '.bmp': ('image', 'image'),
        '.svg': ('image', 'image'),
        '.ico': ('image', 'image'),
        '.webp': ('image', 'image'),
        '.tiff': ('image', 'image'),
        
        # Документы
        '.pdf': ('document', 'file-text'),
        '.doc': ('document', 'file-text'),
        '.docx': ('document', 'file-text'),
        '.txt': ('text', 'file-text'),
        '.rtf': ('document', 'file-text'),
        '.odt': ('document', 'file-text'),
        
        # Таблицы
        '.xls': ('spreadsheet', 'table'),
        '.xlsx': ('spreadsheet', 'table'),
        '.csv': ('spreadsheet', 'table'),
        '.ods': ('spreadsheet', 'table'),
        
        # Презентации
        '.ppt': ('presentation', 'presentation'),
        '.pptx': ('presentation', 'presentation'),
        '.odp': ('presentation', 'presentation'),
        
        # Код
        '.py': ('code', 'code'),
        '.js': ('code', 'code'),
        '.ts': ('code', 'code'),
        '.html': ('code', 'code'),
        '.htm': ('code', 'code'),
        '.css': ('code', 'code'),
        '.scss': ('code', 'code'),
        '.sass': ('code', 'code'),
        '.json': ('code', 'code'),
        '.xml': ('code', 'code'),
        '.yaml': ('code', 'code'),
        '.yml': ('code', 'code'),
        '.php': ('code', 'code'),
        '.java': ('code', 'code'),
        '.cpp': ('code', 'code'),
        '.c': ('code', 'code'),
        '.h': ('code', 'code'),
        '.cs': ('code', 'code'),
        '.rb': ('code', 'code'),
        '.go': ('code', 'code'),
        '.rs': ('code', 'code'),
        '.swift': ('code', 'code'),
        '.kt': ('code', 'code'),
        '.vue': ('code', 'code'),
        '.jsx': ('code', 'code'),
        '.tsx': ('code', 'code'),
        
        # Архивы
        '.zip': ('archive', 'archive'),
        '.rar': ('archive', 'archive'),
        '.7z': ('archive', 'archive'),
        '.tar': ('archive', 'archive'),
        '.gz': ('archive', 'archive'),
        '.bz2': ('archive', 'archive'),
        '.xz': ('archive', 'archive'),
        
        # Аудио
        '.mp3': ('audio', 'music'),
        '.wav': ('audio', 'music'),
        '.flac': ('audio', 'music'),
        '.ogg': ('audio', 'music'),
        '.m4a': ('audio', 'music'),
        '.aac': ('audio', 'music'),
        '.wma': ('audio', 'music'),
        
        # Видео
        '.mp4': ('video', 'video'),
        '.avi': ('video', 'video'),
        '.mkv': ('video', 'video'),
        '.mov': ('video', 'video'),
        '.wmv': ('video', 'video'),
        '.flv': ('video', 'video'),
        '.webm': ('video', 'video'),
        '.m4v': ('video', 'video'),
        
        # Исполняемые файлы
        '.exe': ('executable', 'play'),
        '.msi': ('executable', 'play'),
        '.deb': ('executable', 'play'),
        '.rpm': ('executable', 'play'),
        '.dmg': ('executable', 'play'),
        '.app': ('executable', 'play'),
        
        # Системные файлы
        '.dll': ('system', 'settings'),
        '.so': ('system', 'settings'),
        '.dylib': ('system', 'settings'),
        '.sys': ('system', 'settings'),
        '.ini': ('config', 'settings'),
        '.conf': ('config', 'settings'),
        '.cfg': ('config', 'settings'),
        
        # Шрифты
        '.ttf': ('font', 'type'),
        '.otf': ('font', 'type'),
        '.woff': ('font', 'type'),
        '.woff2': ('font', 'type'),
        '.eot': ('font', 'type'),
        
        # База данных
        '.db': ('database', 'database'),
        '.sqlite': ('database', 'database'),
        '.sqlite3': ('database', 'database'),
        '.mdb': ('database', 'database'),
        
        # Markdown
        '.md': ('markdown', 'file-text'),
        '.markdown': ('markdown', 'file-text'),
        '.rst': ('markdown', 'file-text'),
        
        # Логи
        '.log': ('log', 'file-text'),
        '.txt': ('text', 'file-text'),
    }
    
    @classmethod
    def get_file_type_and_icon(cls, file_path: str) -> tuple[str, str]:
        """
        Определяет тип файла и соответствующую иконку
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Кортеж (тип_файла, имя_иконки)
        """
        if os.path.isdir(file_path):
            return ('folder', 'folder')
        
        # Получаем расширение файла
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Ищем в маппинге
        if ext in cls.FILE_TYPE_MAPPING:
            file_type, icon_name = cls.FILE_TYPE_MAPPING[ext]
            return (file_type, icon_name)
        
        # Проверяем специальные случаи
        filename = os.path.basename(file_path).lower()
        
        # README файлы
        if filename.startswith('readme'):
            return ('readme', 'info')
        
        # Dockerfile
        if filename == 'dockerfile' or filename.startswith('dockerfile.'):
            return ('docker', 'box')
        
        # .gitignore и подобные
        if filename.startswith('.git'):
            return ('git', 'git-branch')
        
        # package.json, requirements.txt и подобные
        if filename in ['package.json', 'package-lock.json', 'yarn.lock']:
            return ('package', 'package')
        
        if filename in ['requirements.txt', 'setup.py', 'pyproject.toml']:
            return ('python-package', 'package')
        
        # Makefile
        if filename in ['makefile', 'make']:
            return ('makefile', 'hammer')
        
        # Скрытые файлы (начинающиеся с точки)
        if filename.startswith('.') and ext == '':
            return ('hidden', 'eye-off')
        
        # По умолчанию - обычный файл
        return ('file', 'file')
    
    @classmethod
    def get_icon_for_file(cls, file_path: str) -> str:
        """
        Получает имя иконки для файла
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Имя иконки
        """
        _, icon_name = cls.get_file_type_and_icon(file_path)
        return icon_name
    
    @classmethod
    def get_file_type(cls, file_path: str) -> str:
        """
        Получает тип файла
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Тип файла
        """
        file_type, _ = cls.get_file_type_and_icon(file_path)
        return file_type
    
    @classmethod
    def is_code_file(cls, file_path: str) -> bool:
        """Проверяет, является ли файл кодом"""
        file_type, _ = cls.get_file_type_and_icon(file_path)
        return file_type == 'code'
    
    @classmethod
    def is_image_file(cls, file_path: str) -> bool:
        """Проверяет, является ли файл изображением"""
        file_type, _ = cls.get_file_type_and_icon(file_path)
        return file_type == 'image'
    
    @classmethod
    def is_document_file(cls, file_path: str) -> bool:
        """Проверяет, является ли файл документом"""
        file_type, _ = cls.get_file_type_and_icon(file_path)
        return file_type in ['document', 'text', 'markdown']
