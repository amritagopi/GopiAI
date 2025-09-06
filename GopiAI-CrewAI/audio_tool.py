from __future__ import annotations

# Optional imports with graceful degradation for type checkers and runtime
try:
    import sounddevice as sd  # type: ignore
    HAS_SOUNDDEVICE = True
except Exception:
    sd = None  # type: ignore[assignment]
    HAS_SOUNDDEVICE = False

try:
    import soundfile as sf  # type: ignore
    HAS_SOUNDFILE = True
except Exception:
    sf = None  # type: ignore[assignment]
    HAS_SOUNDFILE = False


class GopiAIAudioTool:
    def __init__(self, sample_rate: int = 44100, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels

    def _require(self, cond: bool, message: str) -> None:
        if not cond:
            raise RuntimeError(message)

    def record(self, filename: str, duration: float) -> None:
        print(f"Запись аудио в файл {filename} на {duration} секунд...")
        try:
            self._require(HAS_SOUNDDEVICE, "Модуль 'sounddevice' не установлен. Установите: pip install sounddevice")
            self._require(HAS_SOUNDFILE, "Модуль 'soundfile' не установлен. Установите: pip install soundfile")
            # type: ignore[union-attr] because sd/sf could be None at type level
            recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=self.channels)  # type: ignore[union-attr]
            sd.wait()  # type: ignore[union-attr]
            sf.write(filename, recording, self.sample_rate)  # type: ignore[union-attr]
            print("Запись завершена.")
        except Exception as e:
            print(f"Ошибка записи: {e}")

    def play(self, filename: str) -> None:
        print(f"Воспроизведение аудио из файла {filename}...")
        try:
            self._require(HAS_SOUNDDEVICE, "Модуль 'sounddevice' не установлен. Установите: pip install sounddevice")
            self._require(HAS_SOUNDFILE, "Модуль 'soundfile' не установлен. Установите: pip install soundfile")
            data, samplerate = sf.read(filename)  # type: ignore[union-attr]
            sd.play(data, samplerate)  # type: ignore[union-attr]
            sd.wait()  # type: ignore[union-attr]
            print("Воспроизведение завершено.")
        except FileNotFoundError:
            print(f"Файл {filename} не найден.")
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")

    def get_info(self, filename: str):
        try:
            self._require(HAS_SOUNDFILE, "Модуль 'soundfile' не установлен. Установите: pip install soundfile")
            info = sf.info(filename)  # type: ignore[union-attr]
            return info
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Ошибка получения информации о файле: {e}")
            return None


# Пример использования (оставьте закомментированным, чтобы модуль не запускал запись при импорте)
if __name__ == "__main__":
    tool = GopiAIAudioTool()
    # tool.record("recording.wav", 10)  # Запись 10 секунд
    # tool.play("recording.wav")        # Воспроизведение
    # info = tool.get_info("recording.wav")
    # print(info)
