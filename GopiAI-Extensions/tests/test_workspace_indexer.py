"""
Тесты для Smart Workspace Indexer

Проверяет корректность работы системы индексации рабочего пространства.
"""

import os
import json
import tempfile
import shutil
import pytest
from pathlib import Path
from datetime import datetime

from gopiai.extensions.workspace_indexer import (
    SmartWorkspaceIndexer,
    ProjectTypeDetector,
    FileTreeBuilder,
    WorkspaceIndexerCache,
    ProjectInfo,
    FileTreeNode,
    WorkspaceIndex
)

class TestProjectTypeDetector:
    """Тесты для детектора типа проекта"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.detector = ProjectTypeDetector()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_node_project(self):
        """Тест определения Node.js проекта"""
        # Создаём package.json
        package_json = {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.0.0",
                "express": "^4.18.0"
            }
        }
        
        with open(os.path.join(self.temp_dir, 'package.json'), 'w') as f:
            json.dump(package_json, f)
        
        # Создаём JS файлы
        Path(self.temp_dir, 'index.js').touch()
        Path(self.temp_dir, 'app.js').touch()
        
        project_info = self.detector.detect_project_type(self.temp_dir)
        
        assert project_info.project_type == 'node'
        assert project_info.primary_language == 'javascript'
        assert 'React' in project_info.frameworks
        assert 'Express.js' in project_info.frameworks
        assert 'npm' in project_info.package_managers
    
    def test_detect_python_project(self):
        """Тест определения Python проекта"""
        # Создаём requirements.txt
        requirements = "django>=4.0.0\nflask>=2.0.0\nfastapi>=0.70.0"
        
        with open(os.path.join(self.temp_dir, 'requirements.txt'), 'w') as f:
            f.write(requirements)
        
        # Создаём Python файлы
        Path(self.temp_dir, 'main.py').touch()
        Path(self.temp_dir, 'app.py').touch()
        
        project_info = self.detector.detect_project_type(self.temp_dir)
        
        assert project_info.project_type == 'python'
        assert project_info.primary_language == 'python'
        assert 'Django' in project_info.frameworks
        assert 'Flask' in project_info.frameworks
        assert 'FastAPI' in project_info.frameworks
        assert 'pip' in project_info.package_managers
    
    def test_detect_java_project(self):
        """Тест определения Java проекта"""
        # Создаём pom.xml
        pom_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <project>
            <groupId>com.example</groupId>
            <artifactId>test-project</artifactId>
            <version>1.0.0</version>
        </project>"""
        
        with open(os.path.join(self.temp_dir, 'pom.xml'), 'w') as f:
            f.write(pom_xml)
        
        # Создаём Java файлы
        src_dir = Path(self.temp_dir, 'src', 'main', 'java')
        src_dir.mkdir(parents=True)
        (src_dir / 'Main.java').touch()
        
        project_info = self.detector.detect_project_type(self.temp_dir)
        
        assert project_info.project_type == 'java'
        assert project_info.primary_language == 'java'
        assert 'Maven' in project_info.build_tools
    
    def test_detect_mixed_project(self):
        """Тест определения смешанного проекта"""
        # Создаём файлы разных типов
        Path(self.temp_dir, 'package.json').touch()
        Path(self.temp_dir, 'requirements.txt').touch()
        Path(self.temp_dir, 'index.js').touch()
        Path(self.temp_dir, 'main.py').touch()
        
        project_info = self.detector.detect_project_type(self.temp_dir)
        
        # Должен определить основной тип по количеству файлов
        assert project_info.project_type in ['node', 'python']
        assert project_info.primary_language in ['javascript', 'python']

class TestFileTreeBuilder:
    """Тесты для строителя дерева файлов"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.builder = FileTreeBuilder()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_build_simple_tree(self):
        """Тест построения простого дерева"""
        # Создаём структуру файлов
        Path(self.temp_dir, 'file1.txt').touch()
        Path(self.temp_dir, 'file2.js').touch()
        
        subdir = Path(self.temp_dir, 'subdir')
        subdir.mkdir()
        (subdir / 'file3.py').touch()
        
        tree, total_files, total_size = self.builder.build_file_tree(self.temp_dir)
        
        assert tree.is_directory
        assert tree.name == os.path.basename(self.temp_dir)
        assert len(tree.children) == 3  # 2 файла + 1 директория
        assert total_files == 3
    
    def test_gitignore_support(self):
        """Тест поддержки .gitignore"""
        # Создаём .gitignore
        gitignore_content = "*.log\nnode_modules/\n.env"
        
        with open(os.path.join(self.temp_dir, '.gitignore'), 'w') as f:
            f.write(gitignore_content)
        
        # Создаём файлы, которые должны быть проигнорированы
        Path(self.temp_dir, 'app.log').touch()
        Path(self.temp_dir, '.env').touch()
        Path(self.temp_dir, 'normal_file.txt').touch()
        
        node_modules = Path(self.temp_dir, 'node_modules')
        node_modules.mkdir()
        (node_modules / 'package.json').touch()
        
        tree, total_files, total_size = self.builder.build_file_tree(self.temp_dir)
        
        # Должен остаться только normal_file.txt
        file_names = [child.name for child in tree.children if not child.is_directory]
        assert 'normal_file.txt' in file_names
        assert 'app.log' not in file_names
        assert '.env' not in file_names
        
        dir_names = [child.name for child in tree.children if child.is_directory]
        assert 'node_modules' not in dir_names

class TestWorkspaceIndexerCache:
    """Тесты для системы кэширования"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.temp_cache_dir = tempfile.mkdtemp()
        self.cache = WorkspaceIndexerCache(self.temp_cache_dir)
        self.temp_workspace = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        shutil.rmtree(self.temp_cache_dir, ignore_errors=True)
        shutil.rmtree(self.temp_workspace, ignore_errors=True)
    
    def test_cache_save_and_load(self):
        """Тест сохранения и загрузки кэша"""
        # Создаём тестовый индекс
        project_info = ProjectInfo(
            project_type='python',
            primary_language='python',
            technologies=['git'],
            frameworks=['Django'],
            build_tools=['setuptools'],
            package_managers=['pip'],
            config_files=[],
            entry_points=['main.py'],
            test_directories=[],
            documentation_files=['README.md']
        )
        
        file_tree = FileTreeNode(
            name='test_project',
            path=self.temp_workspace,
            is_directory=True,
            children=[]
        )
        
        workspace_index = WorkspaceIndex(
            workspace_path=self.temp_workspace,
            project_info=project_info,
            file_tree=file_tree,
            total_files=1,
            total_size=100,
            indexed_at=datetime.now(),
            cache_key='test_key'
        )
        
        # Сохраняем в кэш
        self.cache.save_index_to_cache(workspace_index)
        
        # Загружаем из кэша
        loaded_index = self.cache.get_cached_index(self.temp_workspace)
        
        assert loaded_index is not None
        assert loaded_index.project_info.project_type == 'python'
        assert loaded_index.project_info.primary_language == 'python'
        assert loaded_index.total_files == 1
        assert loaded_index.total_size == 100
    
    def test_cache_expiration(self):
        """Тест истечения срока действия кэша"""
        # Создаём кэш с истёкшим TTL
        self.cache.cache_ttl = timedelta(seconds=-1)  # Уже истёк
        
        project_info = ProjectInfo(
            project_type='node',
            primary_language='javascript',
            technologies=[],
            frameworks=[],
            build_tools=[],
            package_managers=[],
            config_files=[],
            entry_points=[],
            test_directories=[],
            documentation_files=[]
        )
        
        file_tree = FileTreeNode(
            name='test_project',
            path=self.temp_workspace,
            is_directory=True,
            children=[]
        )
        
        workspace_index = WorkspaceIndex(
            workspace_path=self.temp_workspace,
            project_info=project_info,
            file_tree=file_tree,
            total_files=0,
            total_size=0,
            indexed_at=datetime.now(),
            cache_key='expired_key'
        )
        
        # Сохраняем в кэш
        self.cache.save_index_to_cache(workspace_index)
        
        # Пытаемся загрузить - должен вернуть None из-за истечения TTL
        loaded_index = self.cache.get_cached_index(self.temp_workspace)
        assert loaded_index is None

class TestSmartWorkspaceIndexer:
    """Тесты для основного индексатора"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.temp_cache_dir = tempfile.mkdtemp()
        self.indexer = SmartWorkspaceIndexer(self.temp_cache_dir)
        self.temp_workspace = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        shutil.rmtree(self.temp_cache_dir, ignore_errors=True)
        shutil.rmtree(self.temp_workspace, ignore_errors=True)
    
    def test_full_indexing_workflow(self):
        """Тест полного процесса индексации"""
        # Создаём тестовый проект
        package_json = {
            "name": "test-app",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.0.0"
            }
        }
        
        with open(os.path.join(self.temp_workspace, 'package.json'), 'w') as f:
            json.dump(package_json, f)
        
        Path(self.temp_workspace, 'index.js').touch()
        Path(self.temp_workspace, 'README.md').touch()
        
        src_dir = Path(self.temp_workspace, 'src')
        src_dir.mkdir()
        (src_dir / 'App.js').touch()
        (src_dir / 'index.css').touch()
        
        # Выполняем индексацию
        workspace_index = self.indexer.index_workspace(self.temp_workspace)
        
        # Проверяем результат
        assert workspace_index.project_info.project_type == 'node'
        assert workspace_index.project_info.primary_language == 'javascript'
        assert 'React' in workspace_index.project_info.frameworks
        assert workspace_index.total_files > 0
        assert workspace_index.file_tree.is_directory
    
    def test_caching_behavior(self):
        """Тест поведения кэширования"""
        # Создаём простой проект
        Path(self.temp_workspace, 'main.py').touch()
        
        # Первая индексация
        index1 = self.indexer.index_workspace(self.temp_workspace)
        
        # Вторая индексация (должна использовать кэш)
        index2 = self.indexer.index_workspace(self.temp_workspace)
        
        # Проверяем, что результаты одинаковые
        assert index1.cache_key == index2.cache_key
        assert index1.project_info.project_type == index2.project_info.project_type
    
    def test_force_refresh(self):
        """Тест принудительного обновления"""
        # Создаём проект
        Path(self.temp_workspace, 'main.py').touch()
        
        # Первая индексация
        index1 = self.indexer.index_workspace(self.temp_workspace)
        
        # Добавляем новый файл
        Path(self.temp_workspace, 'new_file.py').touch()
        
        # Принудительное обновление
        index2 = self.indexer.index_workspace(self.temp_workspace, force_refresh=True)
        
        # Количество файлов должно увеличиться
        assert index2.total_files > index1.total_files
    
    def test_project_summary_generation(self):
        """Тест генерации краткого описания проекта"""
        # Создаём проект
        package_json = {
            "name": "test-app",
            "dependencies": {"react": "^18.0.0", "express": "^4.18.0"}
        }
        
        with open(os.path.join(self.temp_workspace, 'package.json'), 'w') as f:
            json.dump(package_json, f)
        
        Path(self.temp_workspace, 'index.js').touch()
        
        # Индексируем
        workspace_index = self.indexer.index_workspace(self.temp_workspace)
        
        # Генерируем описание
        summary = self.indexer.get_project_summary(workspace_index)
        
        assert 'node' in summary
        assert 'javascript' in summary
        assert 'React' in summary or 'Express.js' in summary
    
    def test_llm_context_generation(self):
        """Тест генерации контекста для LLM"""
        # Создаём проект с документацией
        Path(self.temp_workspace, 'main.py').touch()
        Path(self.temp_workspace, 'README.md').touch()
        Path(self.temp_workspace, 'requirements.txt').touch()
        
        # Индексируем
        workspace_index = self.indexer.index_workspace(self.temp_workspace)
        
        # Генерируем контекст
        context = self.indexer.get_context_for_llm(workspace_index)
        
        assert 'КОНТЕКСТ ПРОЕКТА' in context
        assert 'ОБЩАЯ ИНФОРМАЦИЯ' in context
        assert 'СТРУКТУРА ПРОЕКТА' in context
        assert 'python' in context.lower()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])