"""
Smart Workspace Indexer - Интеллектуальная система индексации рабочего пространства

Этот модуль автоматически анализирует проекты и предоставляет контекст для LLM.
Включает определение типа проекта, построение дерева файлов с умными паттернами игнорирования,
обнаружение технологий и кэширование результатов.

Автор: GopiAI System
Версия: 1.0.0
"""

import os
import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import fnmatch
import re

logger = logging.getLogger(__name__)

@dataclass
class ProjectInfo:
    """Информация о проекте"""
    project_type: str
    primary_language: str
    technologies: List[str]
    frameworks: List[str]
    build_tools: List[str]
    package_managers: List[str]
    config_files: List[str]
    entry_points: List[str]
    test_directories: List[str]
    documentation_files: List[str]
    
@dataclass
class FileTreeNode:
    """Узел дерева файлов"""
    name: str
    path: str
    is_directory: bool
    size: Optional[int] = None
    modified: Optional[float] = None
    children: Optional[List['FileTreeNode']] = None
    
@dataclass
class WorkspaceIndex:
    """Полный индекс рабочего пространства"""
    workspace_path: str
    project_info: ProjectInfo
    file_tree: FileTreeNode
    total_files: int
    total_size: int
    indexed_at: datetime
    cache_key: str

class ProjectTypeDetector:
    """Детектор типа проекта"""
    
    # Паттерны для определения типа проекта
    PROJECT_PATTERNS = {
        'node': {
            'files': ['package.json', 'yarn.lock', 'package-lock.json'],
            'directories': ['node_modules'],
            'extensions': ['.js', '.ts', '.jsx', '.tsx']
        },
        'python': {
            'files': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile', 'poetry.lock'],
            'directories': ['__pycache__', '.venv', 'venv', 'env'],
            'extensions': ['.py', '.pyx', '.pyi']
        },
        'java': {
            'files': ['pom.xml', 'build.gradle', 'gradle.properties'],
            'directories': ['src/main/java', 'target', 'build'],
            'extensions': ['.java', '.class', '.jar']
        },
        'csharp': {
            'files': ['*.csproj', '*.sln', 'packages.config'],
            'directories': ['bin', 'obj', 'packages'],
            'extensions': ['.cs', '.csx', '.vb']
        },
        'cpp': {
            'files': ['CMakeLists.txt', 'Makefile', 'configure.ac'],
            'directories': ['build', 'cmake-build-debug'],
            'extensions': ['.cpp', '.c', '.h', '.hpp', '.cc', '.cxx']
        },
        'rust': {
            'files': ['Cargo.toml', 'Cargo.lock'],
            'directories': ['target', 'src'],
            'extensions': ['.rs']
        },
        'go': {
            'files': ['go.mod', 'go.sum'],
            'directories': ['vendor'],
            'extensions': ['.go']
        },
        'php': {
            'files': ['composer.json', 'composer.lock'],
            'directories': ['vendor'],
            'extensions': ['.php', '.phtml']
        },
        'ruby': {
            'files': ['Gemfile', 'Gemfile.lock', '*.gemspec'],
            'directories': ['vendor/bundle'],
            'extensions': ['.rb', '.rake']
        },
        'swift': {
            'files': ['Package.swift', '*.xcodeproj', '*.xcworkspace'],
            'directories': ['.build'],
            'extensions': ['.swift']
        }
    }
    
    # Фреймворки и технологии
    FRAMEWORK_PATTERNS = {
        'react': ['package.json', 'react'],
        'vue': ['package.json', 'vue'],
        'angular': ['package.json', '@angular'],
        'django': ['requirements.txt', 'django', 'manage.py'],
        'flask': ['requirements.txt', 'flask'],
        'fastapi': ['requirements.txt', 'fastapi'],
        'spring': ['pom.xml', 'spring'],
        'express': ['package.json', 'express'],
        'nextjs': ['package.json', 'next'],
        'nuxt': ['package.json', 'nuxt'],
        'svelte': ['package.json', 'svelte'],
        'laravel': ['composer.json', 'laravel'],
        'rails': ['Gemfile', 'rails']
    }
    
    def detect_project_type(self, workspace_path: str) -> ProjectInfo:
        """Определяет тип проекта и собирает информацию"""
        logger.info(f"[WORKSPACE-INDEXER] Определение типа проекта: {workspace_path}")
        
        # Сохраняем путь для использования в других методах
        self.workspace_path = workspace_path
        
        # Сканируем файлы в корне проекта
        root_files = self._get_root_files(workspace_path)
        all_files = self._get_all_files(workspace_path, max_depth=3)
        
        # Определяем основной тип проекта
        project_type = self._detect_primary_type(root_files, all_files)
        primary_language = self._detect_primary_language(all_files)
        
        # Определяем технологии и фреймворки
        technologies = self._detect_technologies(root_files, all_files)
        frameworks = self._detect_frameworks(root_files, all_files)
        build_tools = self._detect_build_tools(root_files, workspace_path)
        package_managers = self._detect_package_managers(root_files)
        
        # Находим важные файлы
        config_files = self._find_config_files(all_files)
        entry_points = self._find_entry_points(all_files, project_type)
        test_directories = self._find_test_directories(all_files)
        documentation_files = self._find_documentation_files(all_files)
        
        project_info = ProjectInfo(
            project_type=project_type,
            primary_language=primary_language,
            technologies=technologies,
            frameworks=frameworks,
            build_tools=build_tools,
            package_managers=package_managers,
            config_files=config_files,
            entry_points=entry_points,
            test_directories=test_directories,
            documentation_files=documentation_files
        )
        
        logger.info(f"[WORKSPACE-INDEXER] Обнаружен проект: {project_type} ({primary_language})")
        logger.info(f"[WORKSPACE-INDEXER] Технологии: {', '.join(technologies)}")
        logger.info(f"[WORKSPACE-INDEXER] Фреймворки: {', '.join(frameworks)}")
        
        return project_info
    
    def _get_root_files(self, workspace_path: str) -> List[str]:
        """Получает список файлов в корне проекта"""
        try:
            return [f for f in os.listdir(workspace_path) 
                   if os.path.isfile(os.path.join(workspace_path, f))]
        except (OSError, PermissionError):
            return []
    
    def _get_all_files(self, workspace_path: str, max_depth: int = 3) -> List[str]:
        """Получает список всех файлов с ограничением глубины"""
        all_files = []
        try:
            for root, dirs, files in os.walk(workspace_path):
                # Ограничиваем глубину поиска
                level = root.replace(workspace_path, '').count(os.sep)
                if level >= max_depth:
                    dirs[:] = []  # Не идём глубже
                    continue
                
                # Пропускаем скрытые и служебные директории
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                          ['node_modules', '__pycache__', 'target', 'build', 'dist']]
                
                for file in files:
                    if not file.startswith('.'):
                        all_files.append(os.path.join(root, file))
        except (OSError, PermissionError):
            pass
        
        return all_files
    
    def _detect_primary_type(self, root_files: List[str], all_files: List[str]) -> str:
        """Определяет основной тип проекта"""
        scores = {}
        
        for project_type, patterns in self.PROJECT_PATTERNS.items():
            score = 0
            
            # Проверяем файлы в корне
            for pattern in patterns['files']:
                if any(fnmatch.fnmatch(f, pattern) for f in root_files):
                    score += 10
            
            # Проверяем расширения файлов
            for ext in patterns['extensions']:
                count = sum(1 for f in all_files if f.endswith(ext))
                score += min(count, 5)  # Максимум 5 баллов за расширения
            
            scores[project_type] = score
        
        # Возвращаем тип с максимальным счётом
        if scores:
            return max(scores, key=scores.get)
        return 'unknown'
    
    def _detect_primary_language(self, all_files: List[str]) -> str:
        """Определяет основной язык программирования"""
        language_counts = {}
        
        language_extensions = {
            'python': ['.py', '.pyx', '.pyi'],
            'javascript': ['.js', '.jsx', '.mjs'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java'],
            'csharp': ['.cs', '.csx'],
            'cpp': ['.cpp', '.c', '.cc', '.cxx'],
            'c': ['.c', '.h'],
            'rust': ['.rs'],
            'go': ['.go'],
            'php': ['.php', '.phtml'],
            'ruby': ['.rb', '.rake'],
            'swift': ['.swift'],
            'kotlin': ['.kt', '.kts'],
            'scala': ['.scala'],
            'html': ['.html', '.htm'],
            'css': ['.css', '.scss', '.sass', '.less'],
            'shell': ['.sh', '.bash', '.zsh']
        }
        
        for file_path in all_files:
            for language, extensions in language_extensions.items():
                if any(file_path.endswith(ext) for ext in extensions):
                    language_counts[language] = language_counts.get(language, 0) + 1
                    break
        
        if language_counts:
            return max(language_counts, key=language_counts.get)
        return 'unknown'
    
    def _detect_technologies(self, root_files: List[str], all_files: List[str]) -> List[str]:
        """Определяет используемые технологии"""
        technologies = set()
        
        # Проверяем по файлам конфигурации
        tech_files = {
            'docker': ['Dockerfile', 'docker-compose.yml', '.dockerignore'],
            'kubernetes': ['*.yaml', '*.yml'],
            'terraform': ['*.tf', '*.tfvars'],
            'ansible': ['playbook.yml', 'ansible.cfg'],
            'webpack': ['webpack.config.js', 'webpack.config.ts'],
            'babel': ['.babelrc', 'babel.config.js'],
            'eslint': ['.eslintrc', '.eslintrc.js', '.eslintrc.json'],
            'prettier': ['.prettierrc', 'prettier.config.js'],
            'jest': ['jest.config.js', 'jest.config.json'],
            'pytest': ['pytest.ini', 'conftest.py'],
            'git': ['.gitignore', '.gitattributes'],
            'vscode': ['.vscode/'],
            'github-actions': ['.github/workflows/']
        }
        
        for tech, patterns in tech_files.items():
            for pattern in patterns:
                if any(fnmatch.fnmatch(f, pattern) for f in root_files):
                    technologies.add(tech)
                elif any(pattern in f for f in all_files):
                    technologies.add(tech)
        
        return list(technologies)
    
    def _detect_frameworks(self, root_files: List[str], all_files: List[str]) -> List[str]:
        """Определяет используемые фреймворки"""
        frameworks = []
        
        # Читаем package.json для Node.js проектов
        if 'package.json' in root_files:
            frameworks.extend(self._detect_node_frameworks(root_files, self.workspace_path))
        
        # Читаем requirements.txt для Python проектов
        if any(f in root_files for f in ['requirements.txt', 'pyproject.toml']):
            frameworks.extend(self._detect_python_frameworks(root_files, self.workspace_path))
        
        return frameworks
    
    def _detect_node_frameworks(self, root_files: List[str], workspace_path: str) -> List[str]:
        """Определяет Node.js фреймворки из package.json"""
        frameworks = []
        
        if 'package.json' not in root_files:
            return frameworks
            
        try:
            package_json_path = os.path.join(workspace_path, 'package.json')
            
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                
            dependencies = {**package_data.get('dependencies', {}), 
                          **package_data.get('devDependencies', {})}
            
            framework_mapping = {
                'react': 'React',
                'vue': 'Vue.js',
                '@angular/core': 'Angular',
                'express': 'Express.js',
                'next': 'Next.js',
                'nuxt': 'Nuxt.js',
                'svelte': 'Svelte',
                'gatsby': 'Gatsby',
                'electron': 'Electron'
            }
            
            for dep, framework in framework_mapping.items():
                if dep in dependencies:
                    frameworks.append(framework)
                    
        except (FileNotFoundError, json.JSONDecodeError, PermissionError):
            pass
            
        return frameworks
    
    def _detect_python_frameworks(self, root_files: List[str], workspace_path: str) -> List[str]:
        """Определяет Python фреймворки из requirements.txt"""
        frameworks = []
        
        framework_mapping = {
            'django': 'Django',
            'flask': 'Flask',
            'fastapi': 'FastAPI',
            'tornado': 'Tornado',
            'pyramid': 'Pyramid',
            'bottle': 'Bottle',
            'streamlit': 'Streamlit',
            'dash': 'Dash'
        }
        
        requirements_files = ['requirements.txt', 'requirements-dev.txt', 'requirements-prod.txt']
        
        for req_file in requirements_files:
            if req_file in root_files:
                try:
                    req_file_path = os.path.join(workspace_path, req_file)
                    with open(req_file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        for package, framework in framework_mapping.items():
                            if package in content:
                                frameworks.append(framework)
                except (FileNotFoundError, PermissionError):
                    continue
        
        return frameworks
    
    def _detect_build_tools(self, root_files: List[str], workspace_path: str) -> List[str]:
        """Определяет инструменты сборки"""
        build_tools = []
        
        build_tool_mapping = {
            'webpack.config.js': 'Webpack',
            'rollup.config.js': 'Rollup',
            'vite.config.js': 'Vite',
            'gulpfile.js': 'Gulp',
            'Gruntfile.js': 'Grunt',
            'Makefile': 'Make',
            'CMakeLists.txt': 'CMake',
            'build.gradle': 'Gradle',
            'pom.xml': 'Maven',
            'Cargo.toml': 'Cargo',
            'setup.py': 'setuptools',
            'pyproject.toml': 'Poetry/setuptools'
        }
        
        for file, tool in build_tool_mapping.items():
            if file in root_files:
                build_tools.append(tool)
        
        return build_tools
    
    def _detect_package_managers(self, root_files: List[str]) -> List[str]:
        """Определяет менеджеры пакетов"""
        package_managers = []
        
        manager_mapping = {
            'package-lock.json': 'npm',
            'yarn.lock': 'yarn',
            'pnpm-lock.yaml': 'pnpm',
            'requirements.txt': 'pip',
            'Pipfile': 'pipenv',
            'poetry.lock': 'poetry',
            'Gemfile': 'bundler',
            'composer.json': 'composer',
            'go.mod': 'go modules',
            'Cargo.lock': 'cargo'
        }
        
        for file, manager in manager_mapping.items():
            if file in root_files:
                package_managers.append(manager)
        
        return package_managers
    
    def _find_config_files(self, all_files: List[str]) -> List[str]:
        """Находит файлы конфигурации"""
        config_patterns = [
            '*.config.js', '*.config.ts', '*.config.json',
            '.env*', '*.ini', '*.conf', '*.cfg',
            'tsconfig.json', 'jsconfig.json',
            '.babelrc*', '.eslintrc*', '.prettierrc*'
        ]
        
        config_files = []
        for file_path in all_files:
            file_name = os.path.basename(file_path)
            for pattern in config_patterns:
                if fnmatch.fnmatch(file_name, pattern):
                    config_files.append(file_path)
                    break
        
        return config_files[:20]  # Ограничиваем количество
    
    def _find_entry_points(self, all_files: List[str], project_type: str) -> List[str]:
        """Находит точки входа в приложение"""
        entry_points = []
        
        entry_patterns = {
            'node': ['index.js', 'app.js', 'main.js', 'server.js', 'src/index.js'],
            'python': ['main.py', 'app.py', 'run.py', 'manage.py', '__main__.py'],
            'java': ['Main.java', 'Application.java'],
            'csharp': ['Program.cs', 'Main.cs'],
            'cpp': ['main.cpp', 'main.c'],
            'go': ['main.go'],
            'rust': ['main.rs', 'lib.rs']
        }
        
        patterns = entry_patterns.get(project_type, [])
        for file_path in all_files:
            file_name = os.path.basename(file_path)
            if file_name in patterns:
                entry_points.append(file_path)
        
        return entry_points
    
    def _find_test_directories(self, all_files: List[str]) -> List[str]:
        """Находит директории с тестами"""
        test_dirs = set()
        test_patterns = ['test', 'tests', '__tests__', 'spec', 'specs']
        
        for file_path in all_files:
            path_parts = Path(file_path).parts
            for part in path_parts:
                if part.lower() in test_patterns:
                    test_dirs.add(str(Path(*path_parts[:path_parts.index(part)+1])))
        
        return list(test_dirs)
    
    def _find_documentation_files(self, all_files: List[str]) -> List[str]:
        """Находит файлы документации"""
        doc_patterns = [
            'README*', 'CHANGELOG*', 'LICENSE*', 'CONTRIBUTING*',
            'INSTALL*', 'USAGE*', 'API*', 'DOCS*',
            '*.md', '*.rst', '*.txt'
        ]
        
        doc_files = []
        for file_path in all_files:
            file_name = os.path.basename(file_path)
            for pattern in doc_patterns:
                if fnmatch.fnmatch(file_name.upper(), pattern.upper()):
                    doc_files.append(file_path)
                    break
        
        return doc_files[:15]  # Ограничиваем количество

class FileTreeBuilder:
    """Строитель дерева файлов с поддержкой .gitignore"""
    
    def __init__(self):
        self.default_ignore_patterns = [
            # Системные файлы
            '.DS_Store', 'Thumbs.db', 'desktop.ini',
            # Временные файлы
            '*.tmp', '*.temp', '*.swp', '*.swo', '*~',
            # Логи
            '*.log', 'logs/', 'log/',
            # Кэш и сборка
            'node_modules/', '__pycache__/', '*.pyc', '*.pyo',
            'target/', 'build/', 'dist/', '.next/', '.nuxt/',
            'bin/', 'obj/', 'out/',
            # IDE файлы
            '.vscode/', '.idea/', '*.suo', '*.user',
            # Переменные окружения
            '.env', '.env.local', '.env.*.local',
            # Зависимости
            'vendor/', 'packages/',
            # Другие
            '.git/', '.svn/', '.hg/'
        ]
    
    def build_file_tree(self, workspace_path: str) -> Tuple[FileTreeNode, int, int]:
        """Строит дерево файлов с учётом .gitignore"""
        logger.info(f"[WORKSPACE-INDEXER] Построение дерева файлов: {workspace_path}")
        
        # Загружаем паттерны игнорирования
        ignore_patterns = self._load_ignore_patterns(workspace_path)
        
        # Строим дерево
        root_node = self._build_tree_recursive(workspace_path, ignore_patterns)
        
        # Подсчитываем статистику
        total_files, total_size = self._calculate_stats(root_node)
        
        logger.info(f"[WORKSPACE-INDEXER] Построено дерево: {total_files} файлов, {total_size} байт")
        
        return root_node, total_files, total_size
    
    def _load_ignore_patterns(self, workspace_path: str) -> List[str]:
        """Загружает паттерны игнорирования из .gitignore"""
        patterns = self.default_ignore_patterns.copy()
        
        gitignore_path = os.path.join(workspace_path, '.gitignore')
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
                logger.info(f"[WORKSPACE-INDEXER] Загружено {len(patterns)} паттернов игнорирования")
            except (OSError, UnicodeDecodeError):
                logger.warning("[WORKSPACE-INDEXER] Не удалось прочитать .gitignore")
        
        return patterns
    
    def _should_ignore(self, path: str, patterns: List[str]) -> bool:
        """Проверяет, должен ли путь быть проигнорирован"""
        name = os.path.basename(path)
        
        for pattern in patterns:
            # Простое сопоставление имени файла
            if fnmatch.fnmatch(name, pattern):
                return True
            # Сопоставление полного пути
            if fnmatch.fnmatch(path, pattern):
                return True
            # Сопоставление директории
            if pattern.endswith('/') and pattern[:-1] in path:
                return True
        
        return False
    
    def _build_tree_recursive(self, path: str, ignore_patterns: List[str], 
                            max_depth: int = 10, current_depth: int = 0) -> FileTreeNode:
        """Рекурсивно строит дерево файлов"""
        if current_depth > max_depth:
            return None
        
        name = os.path.basename(path) or path
        is_directory = os.path.isdir(path)
        
        try:
            stat = os.stat(path)
            size = stat.st_size if not is_directory else None
            modified = stat.st_mtime
        except (OSError, PermissionError):
            size = None
            modified = None
        
        node = FileTreeNode(
            name=name,
            path=path,
            is_directory=is_directory,
            size=size,
            modified=modified,
            children=[]
        )
        
        if is_directory:
            try:
                entries = os.listdir(path)
                entries.sort()  # Сортируем для консистентности
                
                for entry in entries:
                    entry_path = os.path.join(path, entry)
                    
                    # Проверяем игнорирование
                    if self._should_ignore(entry_path, ignore_patterns):
                        continue
                    
                    child_node = self._build_tree_recursive(
                        entry_path, ignore_patterns, max_depth, current_depth + 1
                    )
                    
                    if child_node:
                        node.children.append(child_node)
                        
            except (OSError, PermissionError):
                logger.warning(f"[WORKSPACE-INDEXER] Нет доступа к директории: {path}")
        
        return node
    
    def _calculate_stats(self, node: FileTreeNode) -> Tuple[int, int]:
        """Подсчитывает общее количество файлов и размер"""
        if not node:
            return 0, 0
        
        if not node.is_directory:
            return 1, node.size or 0
        
        total_files = 0
        total_size = 0
        
        if node.children:
            for child in node.children:
                files, size = self._calculate_stats(child)
                total_files += files
                total_size += size
        
        return total_files, total_size

class WorkspaceIndexerCache:
    """Система кэширования для индексатора"""
    
    def __init__(self, cache_dir: str = ".acf/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(minutes=5)  # 5 минут TTL
    
    def _get_cache_key(self, workspace_path: str) -> str:
        """Генерирует ключ кэша для рабочего пространства"""
        # Используем путь и время последней модификации для ключа
        try:
            stat = os.stat(workspace_path)
            mtime = stat.st_mtime
            path_hash = hashlib.md5(workspace_path.encode()).hexdigest()
            return f"workspace_{path_hash}_{int(mtime)}"
        except OSError:
            return hashlib.md5(workspace_path.encode()).hexdigest()
    
    def get_cached_index(self, workspace_path: str) -> Optional[WorkspaceIndex]:
        """Получает индекс из кэша"""
        cache_key = self._get_cache_key(workspace_path)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Проверяем TTL
            indexed_at = datetime.fromisoformat(data['indexed_at'])
            if datetime.now() - indexed_at > self.cache_ttl:
                logger.info("[WORKSPACE-INDEXER] Кэш устарел, требуется обновление")
                return None
            
            # Восстанавливаем объекты из JSON
            project_info = ProjectInfo(**data['project_info'])
            file_tree = self._deserialize_file_tree(data['file_tree'])
            
            workspace_index = WorkspaceIndex(
                workspace_path=data['workspace_path'],
                project_info=project_info,
                file_tree=file_tree,
                total_files=data['total_files'],
                total_size=data['total_size'],
                indexed_at=indexed_at,
                cache_key=cache_key
            )
            
            logger.info(f"[WORKSPACE-INDEXER] Загружен индекс из кэша: {cache_key}")
            return workspace_index
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"[WORKSPACE-INDEXER] Ошибка чтения кэша: {e}")
            return None
    
    def save_index_to_cache(self, workspace_index: WorkspaceIndex) -> None:
        """Сохраняет индекс в кэш"""
        cache_file = self.cache_dir / f"{workspace_index.cache_key}.json"
        
        try:
            data = {
                'workspace_path': workspace_index.workspace_path,
                'project_info': asdict(workspace_index.project_info),
                'file_tree': self._serialize_file_tree(workspace_index.file_tree),
                'total_files': workspace_index.total_files,
                'total_size': workspace_index.total_size,
                'indexed_at': workspace_index.indexed_at.isoformat(),
                'cache_key': workspace_index.cache_key
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[WORKSPACE-INDEXER] Индекс сохранён в кэш: {workspace_index.cache_key}")
            
        except (OSError, json.JSONEncodeError) as e:
            logger.error(f"[WORKSPACE-INDEXER] Ошибка сохранения кэша: {e}")
    
    def _serialize_file_tree(self, node: FileTreeNode) -> Dict:
        """Сериализует дерево файлов в JSON"""
        data = {
            'name': node.name,
            'path': node.path,
            'is_directory': node.is_directory,
            'size': node.size,
            'modified': node.modified
        }
        
        if node.children:
            data['children'] = [self._serialize_file_tree(child) for child in node.children]
        
        return data
    
    def _deserialize_file_tree(self, data: Dict) -> FileTreeNode:
        """Десериализует дерево файлов из JSON"""
        children = None
        if 'children' in data:
            children = [self._deserialize_file_tree(child) for child in data['children']]
        
        return FileTreeNode(
            name=data['name'],
            path=data['path'],
            is_directory=data['is_directory'],
            size=data.get('size'),
            modified=data.get('modified'),
            children=children
        )
    
    def clear_cache(self) -> None:
        """Очищает весь кэш"""
        try:
            for cache_file in self.cache_dir.glob("workspace_*.json"):
                cache_file.unlink()
            logger.info("[WORKSPACE-INDEXER] Кэш очищен")
        except OSError as e:
            logger.error(f"[WORKSPACE-INDEXER] Ошибка очистки кэша: {e}")

class SmartWorkspaceIndexer:
    """Главный класс интеллектуального индексатора рабочего пространства"""
    
    def __init__(self, cache_dir: str = ".acf/cache"):
        self.project_detector = ProjectTypeDetector()
        self.file_tree_builder = FileTreeBuilder()
        self.cache = WorkspaceIndexerCache(cache_dir)
        
        logger.info("[WORKSPACE-INDEXER] Smart Workspace Indexer инициализирован")
    
    def index_workspace(self, workspace_path: str, force_refresh: bool = False) -> WorkspaceIndex:
        """
        Индексирует рабочее пространство
        
        Args:
            workspace_path: Путь к рабочему пространству
            force_refresh: Принудительное обновление кэша
            
        Returns:
            WorkspaceIndex: Полный индекс рабочего пространства
        """
        logger.info(f"[WORKSPACE-INDEXER] Начало индексации: {workspace_path}")
        start_time = time.time()
        
        # Проверяем кэш, если не требуется принудительное обновление
        if not force_refresh:
            cached_index = self.cache.get_cached_index(workspace_path)
            if cached_index:
                logger.info(f"[WORKSPACE-INDEXER] Использован кэшированный индекс")
                return cached_index
        
        # Выполняем полную индексацию
        try:
            # 1. Определяем тип проекта и технологии
            project_info = self.project_detector.detect_project_type(workspace_path)
            
            # 2. Строим дерево файлов
            file_tree, total_files, total_size = self.file_tree_builder.build_file_tree(workspace_path)
            
            # 3. Создаём индекс
            cache_key = self.cache._get_cache_key(workspace_path)
            workspace_index = WorkspaceIndex(
                workspace_path=workspace_path,
                project_info=project_info,
                file_tree=file_tree,
                total_files=total_files,
                total_size=total_size,
                indexed_at=datetime.now(),
                cache_key=cache_key
            )
            
            # 4. Сохраняем в кэш
            self.cache.save_index_to_cache(workspace_index)
            
            elapsed = time.time() - start_time
            logger.info(f"[WORKSPACE-INDEXER] Индексация завершена за {elapsed:.2f}с")
            
            return workspace_index
            
        except Exception as e:
            logger.error(f"[WORKSPACE-INDEXER] Ошибка индексации: {e}")
            raise
    
    def get_project_summary(self, workspace_index: WorkspaceIndex) -> str:
        """Генерирует краткое описание проекта для LLM"""
        project = workspace_index.project_info
        
        summary_parts = [
            f"Проект: {project.project_type} ({project.primary_language})",
            f"Файлов: {workspace_index.total_files}",
            f"Размер: {self._format_size(workspace_index.total_size)}"
        ]
        
        if project.frameworks:
            summary_parts.append(f"Фреймворки: {', '.join(project.frameworks)}")
        
        if project.technologies:
            summary_parts.append(f"Технологии: {', '.join(project.technologies[:5])}")
        
        if project.build_tools:
            summary_parts.append(f"Сборка: {', '.join(project.build_tools)}")
        
        return " | ".join(summary_parts)
    
    def get_file_tree_summary(self, workspace_index: WorkspaceIndex, max_depth: int = 3) -> str:
        """Генерирует краткое описание структуры файлов"""
        def build_tree_text(node: FileTreeNode, depth: int = 0, max_depth: int = 3) -> List[str]:
            if depth > max_depth:
                return []
            
            lines = []
            indent = "  " * depth
            icon = "📁" if node.is_directory else "📄"
            
            lines.append(f"{indent}{icon} {node.name}")
            
            if node.children and depth < max_depth:
                # Показываем только первые 10 элементов на каждом уровне
                for child in node.children[:10]:
                    lines.extend(build_tree_text(child, depth + 1, max_depth))
                
                if len(node.children) > 10:
                    lines.append(f"{indent}  ... и ещё {len(node.children) - 10} элементов")
            
            return lines
        
        tree_lines = build_tree_text(workspace_index.file_tree, max_depth=max_depth)
        return "\n".join(tree_lines[:50])  # Ограничиваем 50 строками
    
    def get_context_for_llm(self, workspace_index: WorkspaceIndex) -> str:
        """Генерирует полный контекст проекта для LLM"""
        context_parts = [
            "=== КОНТЕКСТ ПРОЕКТА ===",
            "",
            "📊 ОБЩАЯ ИНФОРМАЦИЯ:",
            self.get_project_summary(workspace_index),
            "",
            "📁 СТРУКТУРА ПРОЕКТА:",
            self.get_file_tree_summary(workspace_index),
            ""
        ]
        
        project = workspace_index.project_info
        
        if project.entry_points:
            context_parts.extend([
                "🚀 ТОЧКИ ВХОДА:",
                "\n".join(f"  • {ep}" for ep in project.entry_points[:5]),
                ""
            ])
        
        if project.config_files:
            context_parts.extend([
                "⚙️ КОНФИГУРАЦИЯ:",
                "\n".join(f"  • {cf}" for cf in project.config_files[:5]),
                ""
            ])
        
        if project.test_directories:
            context_parts.extend([
                "🧪 ТЕСТЫ:",
                "\n".join(f"  • {td}" for td in project.test_directories[:3]),
                ""
            ])
        
        context_parts.append("=== КОНЕЦ КОНТЕКСТА ===")
        
        return "\n".join(context_parts)
    
    def _format_size(self, size_bytes: int) -> str:
        """Форматирует размер в человекочитаемый вид"""
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} ТБ"
    
    def clear_cache(self) -> None:
        """Очищает кэш индексатора"""
        self.cache.clear_cache()

# Глобальный экземпляр индексатора
_workspace_indexer = None

def get_workspace_indexer() -> SmartWorkspaceIndexer:
    """Получает глобальный экземпляр индексатора"""
    global _workspace_indexer
    if _workspace_indexer is None:
        _workspace_indexer = SmartWorkspaceIndexer()
    return _workspace_indexer

# Экспорт основных классов и функций
__all__ = [
    'SmartWorkspaceIndexer',
    'WorkspaceIndex',
    'ProjectInfo',
    'FileTreeNode',
    'get_workspace_indexer'
]