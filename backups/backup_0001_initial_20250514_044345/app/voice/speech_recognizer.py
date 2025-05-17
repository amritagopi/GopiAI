import os
import time
import threading
from typing import Optional, Callable, List, Dict, Any, Tuple
from pathlib import Path
import tempfile

from faster_whisper import WhisperModel
from app.logger import logger

class SpeechRecognizer:
    """
    Класс для распознавания речи с использованием модели Whisper.
    Поддерживает распознавание из аудиофайлов и из аудио данных в памяти.
    """

    # Путь к каталогу с моделями
    DEFAULT_MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", "whisper")

    def __init__(
        self,
        model_path: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        models_dir: Optional[str] = None,
        language: Optional[str] = None
    ):
        """
        Инициализирует распознаватель речи с заданной моделью.

        Args:
            model_path: Путь к модели или название предустановленной модели
            device: Устройство для вычислений ("cpu", "cuda")
            compute_type: Тип вычислений ("int8", "float16", и т.д.)
            models_dir: Каталог с моделями (если используется локальная модель)
            language: Язык для распознавания (None - автоопределение)
        """
        self.language = language
        self.device = device
        self.compute_type = compute_type

        # Загружаем модель
        if models_dir is None:
            models_dir = self.DEFAULT_MODELS_DIR

        # Проверяем, является ли model_path путем к файлу
        if os.path.isfile(model_path):
            model_file = model_path
        elif os.path.isfile(os.path.join(models_dir, model_path)):
            model_file = os.path.join(models_dir, model_path)
        elif os.path.isfile(os.path.join(models_dir, f"ggml-{model_path}.bin")):
            model_file = os.path.join(models_dir, f"ggml-{model_path}.bin")
        else:
            # Используем название предустановленной модели или полный путь
            model_file = model_path

        try:
            logger.info(f"Загрузка модели Whisper из {model_file}...")
            self.model = WhisperModel(model_file, device=device, compute_type=compute_type)
            logger.info(f"Модель Whisper успешно загружена на устройстве {device}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели Whisper: {e}")
            raise

        self._recognition_thread = None
        self._is_recognizing = False

    def recognize_file(
        self,
        audio_file: str,
        language: Optional[str] = None,
        initial_prompt: Optional[str] = None,
        word_timestamps: bool = False
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Распознает речь из аудио файла.

        Args:
            audio_file: Путь к аудио файлу
            language: Язык для распознавания (None - используется язык по умолчанию)
            initial_prompt: Начальная подсказка для модели
            word_timestamps: Возвращать временные метки слов

        Returns:
            Кортеж (распознанный текст, список сегментов с метаданными)
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Аудио файл не найден: {audio_file}")

        lang = language if language is not None else self.language

        try:
            segments, info = self.model.transcribe(
                audio_file,
                language=lang,
                initial_prompt=initial_prompt,
                word_timestamps=word_timestamps
            )

            text_parts = []
            segments_data = []

            for segment in segments:
                text_parts.append(segment.text)
                segment_dict = {
                    "id": segment.id,
                    "seek": segment.seek,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "tokens": segment.tokens,
                    "temperature": segment.temperature,
                    "avg_logprob": segment.avg_logprob,
                    "compression_ratio": segment.compression_ratio,
                    "no_speech_prob": segment.no_speech_prob
                }

                if word_timestamps and hasattr(segment, "words"):
                    segment_dict["words"] = [
                        {"word": w.word, "start": w.start, "end": w.end, "probability": w.probability}
                        for w in segment.words
                    ]

                segments_data.append(segment_dict)

            full_text = " ".join(text_parts)

            logger.info(f"Распознано аудио из файла {os.path.basename(audio_file)}")
            logger.debug(f"Распознанный текст: {full_text[:100]}...")

            return full_text, segments_data

        except Exception as e:
            logger.error(f"Ошибка при распознавании аудио файла: {e}")
            return "", []

    def recognize_audio_data(
        self,
        audio_data: bytes,
        sample_rate: int = 16000,
        language: Optional[str] = None,
        initial_prompt: Optional[str] = None,
        word_timestamps: bool = False
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Распознает речь из аудио данных в памяти.

        Args:
            audio_data: Байтовый объект с аудио данными
            sample_rate: Частота дискретизации аудио
            language: Язык для распознавания (None - используется язык по умолчанию)
            initial_prompt: Начальная подсказка для модели
            word_timestamps: Возвращать временные метки слов

        Returns:
            Кортеж (распознанный текст, список сегментов с метаданными)
        """
        if not audio_data:
            logger.warning("Отсутствуют аудио данные для распознавания")
            return "", []

        # Сохраняем данные во временный файл
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            # Сохраняем аудио данные во временный файл
            with open(temp_filename, "wb") as f:
                f.write(audio_data)

            # Распознаем речь из файла
            return self.recognize_file(
                temp_filename,
                language=language,
                initial_prompt=initial_prompt,
                word_timestamps=word_timestamps
            )

        except Exception as e:
            logger.error(f"Ошибка при распознавании аудио данных: {e}")
            return "", []
        finally:
            # Удаляем временный файл
            try:
                os.unlink(temp_filename)
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл {temp_filename}: {e}")

    def recognize_async(
        self,
        audio_file_or_data: Any,
        callback: Callable[[str, List[Dict[str, Any]]], None],
        is_file: bool = True,
        sample_rate: int = 16000,
        language: Optional[str] = None,
        initial_prompt: Optional[str] = None,
        word_timestamps: bool = False
    ):
        """
        Асинхронно распознает речь из аудио файла или данных.

        Args:
            audio_file_or_data: Путь к файлу или аудио данные
            callback: Функция обратного вызова для получения результата
            is_file: True, если audio_file_or_data - путь к файлу
            sample_rate: Частота дискретизации (для аудио данных)
            language: Язык для распознавания
            initial_prompt: Начальная подсказка для модели
            word_timestamps: Возвращать временные метки слов
        """
        if self._is_recognizing:
            logger.warning("Распознавание уже выполняется")
            return False

        self._is_recognizing = True

        def recognize_thread():
            try:
                if is_file:
                    result = self.recognize_file(
                        audio_file_or_data,
                        language=language,
                        initial_prompt=initial_prompt,
                        word_timestamps=word_timestamps
                    )
                else:
                    result = self.recognize_audio_data(
                        audio_file_or_data,
                        sample_rate=sample_rate,
                        language=language,
                        initial_prompt=initial_prompt,
                        word_timestamps=word_timestamps
                    )

                callback(*result)

            except Exception as e:
                logger.error(f"Ошибка в потоке распознавания: {e}")
                callback("", [])
            finally:
                self._is_recognizing = False

        self._recognition_thread = threading.Thread(target=recognize_thread)
        self._recognition_thread.daemon = True
        self._recognition_thread.start()

        return True

    def is_recognizing(self) -> bool:
        """Возвращает True, если распознавание выполняется."""
        return self._is_recognizing
