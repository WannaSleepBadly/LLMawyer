import whisper
import os
import asyncio
import logging
from .cuda_manager import cuda_manager

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
        self.device = cuda_manager.get_device()
        self.device_name = cuda_manager.get_device_name()
        self.is_cuda_enabled = cuda_manager.is_cuda_enabled()

    def _load_model(self):
        """Загружает модель Whisper на доступное устройство"""
        try:
            device_info = cuda_manager.get_device_info()
            logger.info(f"Загружаю модель Whisper: {self.model_size}")
            logger.info(f"🎮 Устройство: {device_info['name']} ({device_info['device']})")

            if device_info['is_cuda']:
                logger.info(f"🚀 Использую CUDA для ускорения транскрипции")
                logger.info(f"💾 Память GPU: {device_info['memory_gb']} GB")
            else:
                logger.info("⚠️ CUDA недоступна, используется CPU")

            # Загружаем модель на указанное устройство
            self.model = whisper.load_model(self.model_size, device=self.device)

            logger.info("✅ Модель Whisper успешно загружена")

        except Exception as e:
            logger.error(f"❌ Ошибка загрузки модели Whisper: {e}")
            # Fallback на CPU если CUDA не работает
            if self.is_cuda_enabled:
                logger.warning("🔄 Пытаюсь загрузить модель на CPU...")
                try:
                    self.device = "cpu"
                    self.model = whisper.load_model(self.model_size, device=self.device)
                    logger.info("✅ Модель успешно загружена на CPU")
                except Exception as cpu_error:
                    logger.error(f"❌ Ошибка загрузки на CPU: {cpu_error}")
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
            logger.info(f"🎮 Использую устройство: {self.device_name}")

            # Проверяем существование файла
            if not os.path.exists(voice_file_path):
                raise FileNotFoundError(f"Файл не найден: {voice_file_path}")

            # Lazy load модели при первом обращении
            if self.model is None:
                self._load_model()
            # Выполняем транскрипцию в отдельном потоке, чтобы не блокировать event loop
            result = await asyncio.to_thread(self.model.transcribe, voice_file_path, language="ru")
            transcribed_text = result["text"].strip()

            logger.info(f"✅ Транскрипция завершена. Длина текста: {len(transcribed_text)} символов")
            logger.debug(f"Транскрибированный текст: {transcribed_text[:100]}...")

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

            logger.info(f"Файл скачан успешно, размер: {os.path.getsize(temp_path)} байт")

            # Транскрипция
            text = await self.transcribe_voice_message(temp_path)
            logger.info("✅ Транскрипция завершена")

            return text

        except Exception as e:
            logger.error(f"Ошибка при скачивании/транскрипции: {e}")
            raise

        finally:
            # Удаляем файл в любом случае
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.info("🧹 Временный файл удалён")
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл: {e}")

    def get_device_info(self):
        """Возвращает информацию об используемом устройстве"""
        return {
            "device": str(self.device),
            "device_name": self.device_name,
            "is_cuda_enabled": self.is_cuda_enabled,
            "model_size": self.model_size
        }


_transcriber_singleton = None


def get_transcriber() -> WhisperTranscriber:
    global _transcriber_singleton
    if _transcriber_singleton is None:
        _transcriber_singleton = WhisperTranscriber(model_size="base")
    return _transcriber_singleton
