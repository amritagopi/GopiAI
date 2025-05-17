import pyaudio
import wave
import threading
import numpy as np
import time
from typing import Optional, List, Callable
from app.logger import logger

class AudioRecorder:
    """
    Класс для записи аудио с микрофона с использованием PyAudio.
    Поддерживает запись в фоновом режиме и обработку уровня громкости.
    """

    def __init__(
        self,
        rate: int = 16000,
        channels: int = 1,
        chunk: int = 1024,
        format_type=pyaudio.paInt16,
        device_index: Optional[int] = None
    ):
        """
        Инициализирует аудио рекордер с заданными параметрами.

        Args:
            rate: Частота дискретизации (сэмплы в секунду)
            channels: Количество каналов (1 - моно, 2 - стерео)
            chunk: Размер чанка данных для чтения
            format_type: Формат аудио данных из PyAudio
            device_index: Индекс устройства ввода (None - устройство по умолчанию)
        """
        self.rate = rate
        self.channels = channels
        self.chunk = chunk
        self.format = format_type
        self.device_index = device_index

        self.p = None  # Экземпляр PyAudio
        self.stream = None  # Аудио поток
        self.frames: List[bytes] = []  # Записанные фреймы

        self.recording = False  # Флаг, указывающий на процесс записи
        self.paused = False  # Флаг паузы

        self._record_thread = None  # Поток для записи в фоновом режиме
        self._volume_callback = None  # Callback для обновления уровня громкости
        self._max_silence_duration = 2.0  # Максимальная длительность тишины в секундах
        self._silence_threshold = 700  # Порог тишины
        self._auto_stop = False  # Флаг автоматической остановки при тишине

        # Для отслеживания тишины
        self._last_sound_time = 0

    def list_devices(self) -> List[dict]:
        """
        Возвращает список доступных устройств ввода.

        Returns:
            Список словарей с информацией об устройствах
        """
        devices = []
        p = pyaudio.PyAudio()

        info = p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')

        for i in range(num_devices):
            device_info = p.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                devices.append({
                    'index': i,
                    'name': device_info.get('name'),
                    'channels': device_info.get('maxInputChannels'),
                    'rate': int(device_info.get('defaultSampleRate'))
                })

        p.terminate()
        return devices

    def set_volume_callback(self, callback: Callable[[float], None]):
        """
        Устанавливает callback для обновления уровня громкости.

        Args:
            callback: Функция, принимающая значение громкости (0.0 - 1.0)
        """
        self._volume_callback = callback

    def enable_auto_stop(self, enable: bool = True, silence_threshold: int = 700, max_silence_duration: float = 2.0):
        """
        Включает или выключает автоматическую остановку при тишине.

        Args:
            enable: Включить автоматическую остановку
            silence_threshold: Порог тишины (меньше - чувствительнее)
            max_silence_duration: Максимальная длительность тишины в секундах
        """
        self._auto_stop = enable
        self._silence_threshold = silence_threshold
        self._max_silence_duration = max_silence_duration

    def start_recording(self, background: bool = True):
        """
        Начинает запись аудио.

        Args:
            background: Если True, запись происходит в отдельном потоке
        """
        if self.recording:
            logger.warning("Запись уже запущена.")
            return

        self.recording = True
        self.paused = False
        self.frames = []

        if background:
            self._record_thread = threading.Thread(target=self._record)
            self._record_thread.daemon = True
            self._record_thread.start()
        else:
            self._record()

    def _record(self):
        """Внутренний метод для записи аудио с микрофона."""
        try:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk
            )

            self._last_sound_time = time.time()

            logger.info(f"Начата запись аудио с устройства {self.device_index}")

            while self.recording:
                if not self.paused:
                    data = self.stream.read(self.chunk, exception_on_overflow=False)
                    self.frames.append(data)

                    # Обработка уровня громкости
                    if self._volume_callback or self._auto_stop:
                        audio_data = np.frombuffer(data, dtype=np.int16)
                        volume_norm = np.abs(audio_data).mean()

                        if self._volume_callback:
                            # Нормализуем громкость в диапазон 0.0 - 1.0
                            normalized_volume = min(1.0, volume_norm / 10000.0)
                            self._volume_callback(normalized_volume)

                        # Проверка на тишину для автоматической остановки
                        if self._auto_stop:
                            if volume_norm > self._silence_threshold:
                                self._last_sound_time = time.time()
                            elif time.time() - self._last_sound_time > self._max_silence_duration:
                                logger.info(f"Автоматическая остановка записи из-за тишины ({self._max_silence_duration}с)")
                                self.stop_recording()
                                break
                else:
                    time.sleep(0.1)  # Если на паузе, спим немного

        except Exception as e:
            logger.error(f"Ошибка при записи аудио: {e}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.p:
                self.p.terminate()

    def pause_recording(self):
        """Приостанавливает запись."""
        if self.recording and not self.paused:
            self.paused = True
            logger.info("Запись приостановлена.")

    def resume_recording(self):
        """Возобновляет запись после паузы."""
        if self.recording and self.paused:
            self.paused = False
            self._last_sound_time = time.time()  # Сбрасываем таймер тишины
            logger.info("Запись возобновлена.")

    def stop_recording(self):
        """Останавливает запись и закрывает ресурсы."""
        if not self.recording:
            logger.warning("Запись уже остановлена.")
            return

        self.recording = False

        if self._record_thread:
            self._record_thread.join(timeout=2.0)
            self._record_thread = None

        logger.info("Запись остановлена.")

    def save_recording(self, filename: str):
        """
        Сохраняет записанный аудио в файл.

        Args:
            filename: Путь к файлу для сохранения
        """
        if not self.frames:
            logger.warning("Нет данных для сохранения.")
            return

        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            logger.info(f"Запись сохранена в {filename}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении записи: {e}")
            return False

    def get_audio_data(self) -> bytes:
        """
        Возвращает записанные аудио данные.

        Returns:
            Байтовый объект с аудио данными
        """
        return b''.join(self.frames)
