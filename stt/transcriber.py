import asyncio
import logging
import os

import torch.cuda
import whisper

"""
Модуль транскрипции аудио
"""

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    """Класс для транскрипции голосовых сообщений с помощью Whisper"""

    def __init__(self, model_size="tiny"):
        """
        Инициализация транскриптора

        Args:
            model_size (str): Размер модели Whisper (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        # Модель
        self.model = None

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        """Загружает модель Whisper на доступное устройство"""
        try:
            logger.info(
                f"Загружаю модель Whisper: {self.model_size}. Устройство: {self.device}"
            )

            # Загружаем модель на указанное устройство
            self.model = whisper.load_model(self.model_size, device=self.device)

            logger.info("Модель Whisper успешно загружена")

        except Exception as e:
            logger.error(f"Ошибка загрузки модели Whisper: {e}")
            # Fallback на CPU если CUDA не работает
            if self.device == "cuda":
                logger.warning("Пытаюсь загрузить модель на CPU...")
                try:
                    self.device = "cpu"
                    self.model = whisper.load_model(self.model_size, device=self.device)
                    logger.info("Модель успешно загружена на CPU")
                except Exception as cpu_error:
                    logger.error(f"Ошибка загрузки на CPU: {cpu_error}")
                    raise
            else:
                raise

    async def transcribe_voice_message(self, voice_file_path: str) -> str:
        """
        Транскрибирует голосовое сообщение в текст

        Args:
            voice_file_path (str): Путь к файлу голосового сообщения

        Returns:
            str: Транскрибированный текст
        """
        try:
            logger.info(f"Начинаю транскрипцию файла: {voice_file_path}")

            # Проверяем существование файла
            if not os.path.exists(voice_file_path):
                raise FileNotFoundError(f"Файл не найден: {voice_file_path}")

            # Lazy load модели при первом обращении
            if self.model is None:
                self.load_model()
            # Выполняем транскрипцию в отдельном потоке, чтобы не блокировать event loop
            result = await asyncio.to_thread(
                self.model.transcribe, voice_file_path, language="ru"
            )
            transcribed_text = result["text"].strip()

            logger.info(f"Транскрибированный текст: {transcribed_text[:100]}...")

            return transcribed_text

        except Exception as e:
            logger.error(f"❌ Ошибка транскрипции: {e}")
            raise

    async def download_and_transcribe(self, update, context):
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)

        # Создаём свой безопасный путь
        temp_dir = os.path.join(os.getcwd(), "temp_audio")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.normpath(os.path.join(temp_dir, f"{voice.file_id}.ogg"))

        try:
            logger.info(f"Скачиваю файл в {temp_path}")
            await file.download_to_drive(custom_path=temp_path)
            await asyncio.sleep(0.2)  # ждём, пока система освободит файл

            if not os.path.exists(temp_path):
                raise FileNotFoundError(f"Файл не найден после скачивания: {temp_path}")

            logger.info(
                f"Файл скачан успешно, размер: {os.path.getsize(temp_path)} байт"
            )

            # Транскрипция
            text = await self.transcribe_voice_message(temp_path)

            return text

        except Exception as e:
            logger.error(f"Ошибка при скачивании/транскрипции: {e}")
            raise

        finally:
            # Удаляем файл в любом случае
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.info("Временный файл удалён")
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл: {e}")

    def get_device_info(self):
        """Возвращает информацию об используемом устройстве"""
        return {
            "device": str(self.device),
            "model_size": self.model_size,
        }
