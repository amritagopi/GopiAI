import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from PySide6.QtCore import QObject, QMetaMethod, Signal, QTimer

logger = logging.getLogger(__name__)

class SignalConnectionChecker:
    """
    Утилита для обнаружения и проверки подключений сигналов Qt в приложении.
    Помогает обнаружить неподключенные сигналы и проблемы с сигнал-слот соединениями.
    """

    def __init__(self, app_instance=None):
        """
        Инициализирует проверку сигналов.

        Args:
            app_instance: Экземпляр QApplication или главное окно приложения.
        """
        self.app_instance = app_instance
        self.signal_registry = {}  # Хранилище информации о сигналах
        self.unconnected_signals = {}  # Неподключенные сигналы
        self.connection_registry = {}  # Информация о подключениях

    def check_signal_connections(self, start_object: QObject = None) -> Dict[str, List[str]]:
        """
        Рекурсивно проверяет сигналы всех QObject'ов, начиная с указанного объекта.

        Args:
            start_object: Начальный объект для проверки, если None - используется app_instance

        Returns:
            Словарь с информацией о неподключенных сигналах
        """
        if start_object is None:
            if self.app_instance is None:
                logger.error("Не указан начальный объект для проверки сигналов")
                return {}
            start_object = self.app_instance

        # Очищаем предыдущие результаты
        self.unconnected_signals = {}

        # Запускаем рекурсивный обход объектов
        self._inspect_object_signals(start_object)

        # Выводим информацию о найденных проблемах
        self._log_unconnected_signals()

        return self.unconnected_signals

    def _inspect_object_signals(self, obj: QObject, parent_path: str = ""):
        """
        Проверяет сигналы объекта и рекурсивно обходит его дочерние объекты.

        Args:
            obj: Объект для проверки
            parent_path: Путь к родительскому объекту в иерархии
        """
        if obj is None:
            return

        # Формируем путь к объекту
        obj_name = obj.objectName() or obj.__class__.__name__
        current_path = f"{parent_path}.{obj_name}" if parent_path else obj_name

        # Получаем метаобъект для доступа к сигналам
        meta_obj = obj.metaObject()

        # Проверяем сигналы через метаобъект
        for i in range(meta_obj.methodCount()):
            method = meta_obj.method(i)

            # Проверяем только сигналы
            if method.methodType() == QMetaMethod.MethodType.Signal:
                signal_name = method.name().data().decode()
                signature = method.methodSignature().data().decode()

                # Проверяем подключен ли сигнал
                if hasattr(obj, "isSignalConnected"):
                    is_connected = obj.isSignalConnected(method)

                    # Регистрируем информацию о сигнале
                    signal_info = {
                        "name": signal_name,
                        "signature": signature,
                        "connected": is_connected,
                        "object": obj
                    }

                    self.signal_registry[f"{current_path}.{signal_name}"] = signal_info

                    # Если сигнал не подключен, добавляем в список неподключенных
                    if not is_connected:
                        if current_path not in self.unconnected_signals:
                            self.unconnected_signals[current_path] = []
                        self.unconnected_signals[current_path].append(f"{signal_name} ({signature})")

        # Рекурсивно проверяем дочерние объекты
        for child in obj.children():
            self._inspect_object_signals(child, current_path)

    def _log_unconnected_signals(self):
        """Выводит информацию о неподключенных сигналах в лог."""
        if not self.unconnected_signals:
            logger.info("Неподключенных сигналов не обнаружено.")
            return

        logger.warning(f"Обнаружено {sum(len(signals) for signals in self.unconnected_signals.values())} неподключенных сигналов:")

        for obj_path, signals in self.unconnected_signals.items():
            logger.warning(f"  {obj_path}:")
            for signal_info in signals:
                logger.warning(f"    - {signal_info}")

    def suggest_connections(self) -> Dict[str, List[str]]:
        """
        Анализирует неподключенные сигналы и предлагает возможные соединения.

        Returns:
            Словарь с предложениями по подключению сигналов.
        """
        suggestions = {}

        # Распространенные паттерны сигнал-слот
        common_patterns = {
            "clicked": ["on_clicked", "handle_click"],
            "triggered": ["on_triggered", "handle_action"],
            "textChanged": ["on_text_changed", "text_updated"],
            "valueChanged": ["on_value_changed", "value_updated"],
            "stateChanged": ["on_state_changed", "state_updated"],
            "currentIndexChanged": ["on_index_changed", "index_updated"],
            "message_sent": ["handle_message", "on_message_received"],
            "insert_code_to_editor": ["insert_code", "on_code_insert"],
            "run_code_in_terminal": ["execute_command", "run_command"],
        }

        for obj_path, signals in self.unconnected_signals.items():
            suggestions[obj_path] = []

            for signal_info in signals:
                signal_name = signal_info.split(' ')[0]

                # Предлагаем стандартные обработчики по паттернам
                if signal_name in common_patterns:
                    for handler in common_patterns[signal_name]:
                        suggestions[obj_path].append(f"{signal_name} → {handler}")
                else:
                    # Для нестандартных сигналов предлагаем шаблон "on_signal_name"
                    handler = f"on_{signal_name.lower()}"
                    suggestions[obj_path].append(f"{signal_name} → {handler}")

        return suggestions

    def connect_signals_automatically(self) -> int:
        """
        Автоматически создает соединения для неподключенных сигналов.
        Использует паттерны именования для определения подходящих слотов.

        Returns:
            Количество автоматически подключенных сигналов.
        """
        count = 0
        suggestions = self.suggest_connections()

        for obj_path, signals in suggestions.items():
            # Находим объект по пути
            obj = self._find_object_by_path(obj_path)
            if obj is None:
                continue

            for suggestion in signals:
                signal_name, handler_name = suggestion.split(' → ')

                # Проверяем, существует ли метод-обработчик в объекте
                if hasattr(obj, handler_name):
                    handler = getattr(obj, handler_name)

                    # Проверяем, что это вызываемый объект
                    if callable(handler):
                        # Получаем сигнал
                        if hasattr(obj, signal_name):
                            signal = getattr(obj, signal_name)

                            # Подключаем сигнал к обработчику
                            signal.connect(handler)
                            count += 1
                            logger.info(f"Автоматически подключен сигнал: {obj_path}.{signal_name} → {handler_name}")

        return count

    def _find_object_by_path(self, path: str) -> Optional[QObject]:
        """
        Находит объект по его пути в иерархии.

        Args:
            path: Путь к объекту (например: "MainWindow.centralWidget.button1")

        Returns:
            Найденный объект или None, если объект не найден.
        """
        if self.app_instance is None:
            return None

        parts = path.split('.')
        current = self.app_instance

        # Пропускаем первую часть, если это имя корневого объекта
        start_idx = 1 if parts[0] == self.app_instance.objectName() or parts[0] == self.app_instance.__class__.__name__ else 0

        for i in range(start_idx, len(parts)):
            found = False
            part = parts[i]

            # Ищем среди дочерних объектов
            for child in current.children():
                if child.objectName() == part or child.__class__.__name__ == part:
                    current = child
                    found = True
                    break

            if not found:
                return None

        return current


class SignalMonitor(QObject):
    """
    Монитор сигналов для отслеживания отправленных, но не полученных сигналов.
    Позволяет обнаруживать неподключенные сигналы во время выполнения.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sent_signals = set()  # Отправленные сигналы
        self.received_signals = set()  # Полученные сигналы
        self.connected_objects = set()  # Подключенные объекты для мониторинга

        # Таймер для периодической проверки неполученных сигналов
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_unreceived_signals)
        self.check_timer.start(5000)  # Проверка каждые 5 секунд

    def install_on_object(self, obj: QObject):
        """
        Устанавливает мониторинг на объект и его сигналы.

        Args:
            obj: Объект QObject для мониторинга
        """
        if obj in self.connected_objects:
            return

        self.connected_objects.add(obj)

        # Перехватываем все сигналы объекта
        meta_obj = obj.metaObject()
        for i in range(meta_obj.methodCount()):
            method = meta_obj.method(i)
            if method.methodType() == QMetaMethod.MethodType.Signal:
                signal_name = method.name().data().decode()

                # Перехватывать сигналы - это сложная задача и требует
                # специальных подходов, зависящих от конкретного приложения
                # Это демонстрационный код, который на практике нужно дополнить

    def record_signal_sent(self, obj: QObject, signal_name: str):
        """
        Записывает факт отправки сигнала.

        Args:
            obj: Объект, отправивший сигнал
            signal_name: Имя отправленного сигнала
        """
        obj_id = id(obj)
        signal_id = f"{obj_id}:{signal_name}"
        self.sent_signals.add(signal_id)

    def record_signal_received(self, obj: QObject, signal_name: str):
        """
        Записывает факт получения сигнала.

        Args:
            obj: Объект, получивший сигнал
            signal_name: Имя полученного сигнала
        """
        obj_id = id(obj)
        signal_id = f"{obj_id}:{signal_name}"
        self.received_signals.add(signal_id)

    def check_unreceived_signals(self):
        """Проверяет сигналы, которые были отправлены, но не были получены."""
        unreceived = self.sent_signals - self.received_signals

        if unreceived:
            logger.warning(f"Обнаружено {len(unreceived)} сигналов, которые были отправлены, но не получены:")
            for signal_id in unreceived:
                logger.warning(f"  - {signal_id}")


# Вспомогательная функция для проверки сигналов в главном окне
def check_main_window_signals(main_window):
    """
    Проверяет сигналы в главном окне и его компонентах.

    Args:
        main_window: Экземпляр главного окна приложения

    Returns:
        Словарь с информацией о неподключенных сигналах
    """
    checker = SignalConnectionChecker(main_window)
    unconnected = checker.check_signal_connections()

    if unconnected:
        logger.warning("Найдены неподключенные сигналы. Рекомендуется проверить соединения.")
        suggestions = checker.suggest_connections()

        for obj_path, signal_suggestions in suggestions.items():
            logger.info(f"Предложения для {obj_path}:")
            for suggestion in signal_suggestions:
                logger.info(f"  - {suggestion}")

    return unconnected

def auto_connect_signals(main_window):
    """
    Автоматически подключает неподключенные сигналы по шаблонам имен.

    Args:
        main_window: Экземпляр главного окна приложения

    Returns:
        tuple: (Количество подключенных сигналов, словарь с подключениями)
    """
    try:
        # Создаем экземпляр проверки сигналов
        checker = SignalConnectionChecker(main_window)

        # Сначала находим неподключенные сигналы
        unconnected_signals = checker.check_signal_connections()

        if not unconnected_signals:
            logger.info("Неподключенных сигналов не найдено, нечего подключать.")
            return 0, {}

        # Автоматически соединяем сигналы, если возможно
        connected_count = checker.connect_signals_automatically()

        # Получаем информацию о выполненных соединениях
        connections_info = {}
        for key, value in checker.signal_registry.items():
            if hasattr(value, "connected") and value["connected"] is True:
                obj_name = key.rsplit('.', 1)[0]
                if obj_name not in connections_info:
                    connections_info[obj_name] = []
                connections_info[obj_name].append(value["name"])

        return connected_count, connections_info

    except Exception as e:
        logger.error(f"Ошибка при автоматическом подключении сигналов: {e}")
        return 0, {}
