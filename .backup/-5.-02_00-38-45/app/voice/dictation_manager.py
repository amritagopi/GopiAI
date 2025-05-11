import os
import time
from typing import Optional, Callable, Dict, List, Any
from PySide6.QtCore import QObject, Signal, Slot

from app.voice.audio_recorder import AudioRecorder
from app.voice.speech_recognizer import SpeechRecognizer
from app.logger import logger


class DictationManager(QObject):
    """
    Менеджер диктовки, объединяющий запись и распознавание речи.
    Предоставляет интерфейс для голосового ввода текста.
    """

    # Сигналы для уведомления о статусе и результатах диктовки
    recordingStarted = Signal()
    recordingStopped = Signal()
    recordingPaused = Signal()
    recordingResumed = Signal()
    volumeChanged = Signal(float)  # Уровень громкости (0.0 - 1.0)
    transcribing = Signal()  # Началось распознавание
    transcriptionComplete = Signal(str)  # Распознанный текст
    transcriptionError = Signal(str)  # Ошибка распознавания

    def __init__(
        self,
        model_path: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        models_dir: Optional[str] = None,
        language: Optional[str] = None,
        auto_language_detection: bool = True,
        parent: Optional[QObject] = None
    ):
        """
        Инициализирует менеджер диктовки.

        Args:
            model_path: Путь к модели или название предустановленной модели
            device: Устройство для вычислений ("cpu", "cuda")
            compute_type: Тип вычислений ("int8", "float16", и т.д.)
            models_dir: Каталог с моделями (если используется локальная модель)
            language: Язык для распознавания (None - автоопределение)
            auto_language_detection: Автоматически определять язык
            parent: Родительский объект QObject
        """
        super().__init__(parent)

        # Создаем экземпляры рекордера и распознавателя
        self.recorder = AudioRecorder()

        # Настраиваем callback для обновления уровня громкости
        self.recorder.set_volume_callback(self._volume_callback)

        # Язык для распознавания
        self.language = language
        self.auto_language_detection = auto_language_detection

        try:
            # Инициализируем распознаватель речи
            self.recognizer = SpeechRecognizer(
                model_path=model_path,
                device=device,
                compute_type=compute_type,
                models_dir=models_dir,
                language=None if auto_language_detection else language
            )
            logger.info("Менеджер диктовки инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации распознавателя речи: {e}")
            self.recognizer = None
            raise

        # Состояние диктовки
        self.is_recording = False
        self.is_paused = False
        self.is_transcribing = False

        # Временный файл для сохранения записи
        self.temp_audio_file = None

        # Каталог для временных файлов
        self.temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp")
        os.makedirs(self.temp_dir, exist_ok=True)

    def _volume_callback(self, volume: float):
        """Обработчик изменения уровня громкости."""
        self.volumeChanged.emit(volume)

    def start_dictation(self, auto_stop: bool = True, max_silence_duration: float = 2.0):
        """
        Начинает запись для диктовки.

        Args:
            auto_stop: Автоматически останавливать запись при обнаружении тишины
            max_silence_duration: Максимальная длительность тишины в секундах
        """
        if self.is_recording:
            logger.warning("Диктовка уже запущена")
            return

        if self.is_transcribing:
            logger.warning("Идет распознавание предыдущей записи")
            return

        # Включаем автоматическую остановку при тишине
        if auto_stop:
            self.recorder.enable_auto_stop(True, max_silence_duration=max_silence_duration)
        else:
            self.recorder.enable_auto_stop(False)

        # Начинаем запись
        self.recorder.start_recording(background=True)
        self.is_recording = True
        self.is_paused = False

        # Уведомляем о начале записи
        self.recordingStarted.emit()
        logger.info("Начата диктовка")

    def pause_dictation(self):
        """Приостанавливает запись."""
        if self.is_recording and not self.is_paused:
            self.recorder.pause_recording()
            self.is_paused = True
            self.recordingPaused.emit()
            logger.info("Диктовка приостановлена")

    def resume_dictation(self):
        """Возобновляет запись после паузы."""
        if self.is_recording and self.is_paused:
            self.recorder.resume_recording()
            self.is_paused = False
            self.recordingResumed.emit()
            logger.info("Диктовка возобновлена")

    def stop_dictation(self, transcribe: bool = True):
        """
        Останавливает запись и опционально запускает распознавание.

        Args:
            transcribe: Если True, автоматически запускает распознавание
        """
        if not self.is_recording:
            logger.warning("Диктовка не запущена")
            return

        # Останавливаем запись
        self.recorder.stop_recording()
        self.is_recording = False
        self.is_paused = False

        # Уведомляем об остановке записи
        self.recordingStopped.emit()
        logger.info("Диктовка остановлена")

        # Если нужно распознать, запускаем распознавание
        if transcribe:
            self.transcribe_recording()

    def transcribe_recording(self):
        """Запускает распознавание последней записи."""
        if self.is_recording:
            logger.warning("Невозможно распознать: диктовка еще не завершена")
            return

        if self.is_transcribing:
            logger.warning("Распознавание уже выполняется")
            return

        if not self.recognizer:
            self.transcriptionError.emit("Распознаватель речи не инициализирован")
            return

        # Получаем аудио данные
        audio_data = self.recorder.get_audio_data()

        if not audio_data:
            logger.warning("Нет данных для распознавания")
            self.transcriptionError.emit("Нет аудио данных для распознавания")
            return

        # Сохраняем во временный файл для отладки (опционально)
        timestamp = int(time.time())
        self.temp_audio_file = os.path.join(self.temp_dir, f"dictation_{timestamp}.wav")
        self.recorder.save_recording(self.temp_audio_file)

        # Уведомляем о начале распознавания
        self.is_transcribing = True
        self.transcribing.emit()

        # Запускаем распознавание асинхронно
        lang = None if self.auto_language_detection else self.language

        self.recognizer.recognize_async(
            audio_data,
            callback=self._transcription_callback,
            is_file=False,
            language=lang
        )

    def _transcription_callback(self, text: str, segments: List[Dict[str, Any]]):
        """Callback для получения результата распознавания."""
        self.is_transcribing = False

        if text:
            logger.info(f"Распознавание завершено, получен текст длиной {len(text)} символов")
            self.transcriptionComplete.emit(text)
        else:
            logger.warning("Распознавание не дало результатов")
            self.transcriptionError.emit("Не удалось распознать речь")

    def get_available_devices(self) -> List[Dict[str, Any]]:
        """
        Возвращает список доступных устройств ввода.

        Returns:
            Список словарей с информацией об устройствах
        """
        return self.recorder.list_devices()

    def set_input_device(self, device_index: int):
        """
        Устанавливает устройство ввода по его индексу.

        Args:
            device_index: Индекс устройства ввода
        """
        # Сохраняем текущее состояние
        was_recording = self.is_recording
        was_paused = self.is_paused

        # Если идет запись, останавливаем её
        if was_recording:
            self.recorder.stop_recording()
            self.is_recording = False
            self.is_paused = False
            self.recordingStopped.emit()

        # Создаем новый рекордер с выбранным устройством
        self.recorder = AudioRecorder(device_index=device_index)
        self.recorder.set_volume_callback(self._volume_callback)

        # Если запись была запущена, восстанавливаем её
        if was_recording:
            self.recorder.start_recording(background=True)
            self.is_recording = True

            if was_paused:
                self.recorder.pause_recording()
                self.is_paused = True

            self.recordingStarted.emit()

        logger.info(f"Установлено устройство ввода с индексом {device_index}")

    def set_language(self, language: Optional[str]):
        """
        Устанавливает язык для распознавания.

        Args:
            language: Код языка (например, "ru", "en") или None для автоопределения
        """
        self.language = language
        logger.info(f"Установлен язык распознавания: {language if language else 'автоопределение'}")

    def set_auto_language_detection(self, auto_detect: bool):
        """
        Включает или выключает автоматическое определение языка.

        Args:
            auto_detect: True для автоопределения языка
        """
        self.auto_language_detection = auto_detect
        logger.info(f"Автоопределение языка: {'включено' if auto_detect else 'выключено'}")

    def cleanup(self):
        """Освобождает ресурсы."""
        if self.is_recording:
            self.recorder.stop_recording()
            self.is_recording = False
            self.is_paused = False

        # Удаляем временные файлы
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            try:
                os.unlink(self.temp_audio_file)
                self.temp_audio_file = None
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл: {e}")

        logger.info("Ресурсы менеджера диктовки освобождены")
