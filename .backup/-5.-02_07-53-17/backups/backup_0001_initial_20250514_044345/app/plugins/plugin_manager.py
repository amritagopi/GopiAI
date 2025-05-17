import os
import importlib
import logging
import pkgutil
from typing import Dict, List, Any, Optional

from PySide6.QtCore import QObject, Signal

from app.plugins.plugin_base import PluginBase

logger = logging.getLogger(__name__)

class PluginManager(QObject):
    """
    Менеджер плагинов приложения.
    Отвечает за обнаружение, загрузку и управление плагинами.
    """

    # Сигналы
    pluginLoaded = Signal(str)  # Сигнал о загрузке плагина, передает имя плагина
    pluginUnloaded = Signal(str)  # Сигнал о выгрузке плагина, передает имя плагина

    _instance = None

    @classmethod
    def instance(cls):
        """Возвращает единственный экземпляр класса (синглтон)."""
        if cls._instance is None:
            cls._instance = PluginManager()
        return cls._instance

    def __init__(self):
        """
        Инициализирует менеджер плагинов.
        """
        if PluginManager._instance is not None:
            raise RuntimeError("PluginManager уже инициализирован. Используйте PluginManager.instance().")
        
        super().__init__()
        
        # Словарь загруженных плагинов
        self.plugins: Dict[str, PluginBase] = {}
        
        # Список всех доступных плагинов
        self.available_plugins: List[Dict[str, Any]] = []
        
        # Главное окно приложения
        self.main_window = None

    def set_main_window(self, main_window):
        """
        Устанавливает ссылку на главное окно приложения.
        
        Args:
            main_window: Экземпляр главного окна
        """
        self.main_window = main_window

    def discover_plugins(self):
        """
        Обнаруживает все доступные плагины в директории plugins.
        """
        logger.info("Начинаем поиск плагинов...")
        
        self.available_plugins = []
        
        # Получаем путь к каталогу plugins
        plugin_dir = os.path.dirname(__file__)
        
        # Итерируемся по всем модулям в директории plugins
        for _, name, is_pkg in pkgutil.iter_modules([plugin_dir]):
            if is_pkg:
                continue  # Пропускаем пакеты
                
            if name == "plugin_base" or name == "plugin_manager":
                continue  # Пропускаем базовые классы
                
            try:
                # Импортируем модуль
                module_name = f"app.plugins.{name}"
                module = importlib.import_module(module_name)
                
                # Ищем классы, наследующиеся от PluginBase
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    # Проверяем, является ли атрибут классом, наследуемым от PluginBase
                    if (isinstance(attr, type) and 
                        issubclass(attr, PluginBase) and 
                        attr != PluginBase):
                        
                        # Создаем экземпляр для получения метаданных
                        try:
                            plugin_instance = attr()
                            metadata = plugin_instance.metadata()
                            
                            logger.info(f"Найден плагин: {metadata['name']} ({metadata['display_name']})")
                            
                            # Добавляем информацию о плагине
                            self.available_plugins.append({
                                "name": metadata["name"],
                                "display_name": metadata["display_name"],
                                "description": metadata["description"],
                                "version": metadata["version"],
                                "author": metadata["author"],
                                "module": module_name,
                                "class": attr_name,
                                "loaded": False
                            })
                            
                        except Exception as e:
                            logger.error(f"Ошибка при создании экземпляра плагина {attr_name}: {e}")
                
            except Exception as e:
                logger.error(f"Ошибка при обнаружении плагина {name}: {e}")
        
        logger.info(f"Обнаружено плагинов: {len(self.available_plugins)}")
        return self.available_plugins

    def load_plugin(self, plugin_name: str) -> bool:
        """
        Загружает плагин по его имени.
        
        Args:
            plugin_name: Имя плагина для загрузки
            
        Returns:
            True, если плагин успешно загружен, иначе False
        """
        # Проверяем, загружен ли плагин
        if plugin_name in self.plugins:
            logger.warning(f"Плагин {plugin_name} уже загружен")
            return True
        
        # Ищем плагин в доступных
        plugin_info = None
        for info in self.available_plugins:
            if info["name"] == plugin_name:
                plugin_info = info
                break
        
        if not plugin_info:
            logger.error(f"Плагин {plugin_name} не найден")
            return False
        
        try:
            # Импортируем модуль и создаем экземпляр плагина
            module = importlib.import_module(plugin_info["module"])
            plugin_class = getattr(module, plugin_info["class"])
            plugin = plugin_class()
            
            # Инициализируем плагин
            if self.main_window:
                plugin.initialize(self.main_window)
            
            # Добавляем плагин в словарь загруженных плагинов
            self.plugins[plugin_name] = plugin
            
            # Обновляем статус плагина
            for info in self.available_plugins:
                if info["name"] == plugin_name:
                    info["loaded"] = True
                    break
            
            # Уведомляем о загрузке плагина
            self.pluginLoaded.emit(plugin_name)
            
            logger.info(f"Плагин {plugin_name} успешно загружен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке плагина {plugin_name}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Выгружает плагин по его имени.
        
        Args:
            plugin_name: Имя плагина для выгрузки
            
        Returns:
            True, если плагин успешно выгружен, иначе False
        """
        # Проверяем, загружен ли плагин
        if plugin_name not in self.plugins:
            logger.warning(f"Плагин {plugin_name} не загружен")
            return False
        
        try:
            # Получаем экземпляр плагина
            plugin = self.plugins[plugin_name]
            
            # Очищаем ресурсы плагина
            plugin.cleanup()
            
            # Удаляем плагин из словаря загруженных плагинов
            del self.plugins[plugin_name]
            
            # Обновляем статус плагина
            for info in self.available_plugins:
                if info["name"] == plugin_name:
                    info["loaded"] = False
                    break
            
            # Уведомляем о выгрузке плагина
            self.pluginUnloaded.emit(plugin_name)
            
            logger.info(f"Плагин {plugin_name} успешно выгружен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при выгрузке плагина {plugin_name}: {e}")
            return False

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """
        Возвращает экземпляр загруженного плагина по его имени.
        
        Args:
            plugin_name: Имя плагина
            
        Returns:
            Экземпляр плагина или None, если плагин не загружен
        """
        return self.plugins.get(plugin_name)

    def get_loaded_plugins(self) -> Dict[str, PluginBase]:
        """
        Возвращает словарь всех загруженных плагинов.
        
        Returns:
            Словарь загруженных плагинов
        """
        return self.plugins.copy()

    def load_all_plugins(self) -> int:
        """
        Загружает все доступные плагины.
        
        Returns:
            Количество успешно загруженных плагинов
        """
        logger.info("Загрузка всех доступных плагинов...")
        
        if not self.available_plugins:
            self.discover_plugins()
        
        loaded_count = 0
        for info in self.available_plugins:
            if self.load_plugin(info["name"]):
                loaded_count += 1
        
        logger.info(f"Загружено плагинов: {loaded_count} из {len(self.available_plugins)}")
        return loaded_count

    def unload_all_plugins(self) -> int:
        """
        Выгружает все загруженные плагины.
        
        Returns:
            Количество успешно выгруженных плагинов
        """
        logger.info("Выгрузка всех плагинов...")
        
        unloaded_count = 0
        plugins_to_unload = list(self.plugins.keys())
        
        for plugin_name in plugins_to_unload:
            if self.unload_plugin(plugin_name):
                unloaded_count += 1
        
        logger.info(f"Выгружено плагинов: {unloaded_count}")
        return unloaded_count

    def save_plugin_settings(self):
        """
        Сохраняет настройки всех загруженных плагинов.
        """
        logger.info("Сохранение настроек всех плагинов...")
        
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.save_settings()
                logger.debug(f"Настройки плагина {plugin_name} сохранены")
            except Exception as e:
                logger.error(f"Ошибка при сохранении настроек плагина {plugin_name}: {e}")