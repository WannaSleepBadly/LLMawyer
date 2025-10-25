import whisper
import os
import tempfile
import logging
from telegram import Update
from .cuda_manager import cuda_manager

logger = logging.getLogger(__name__)

class WhisperTranscriber:
    """Класс для транскрипции голосовых сообщений с помощью Whisper"""
    
    def __init__(self, model_size="base"):
        """
        Инициализация транскриптора
        
        Args:
            model_size (str): Размер модели Whisper (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self.device = cuda_manager.get_device()
        self.device_name = cuda_manager.get_device_name()
        self.is_cuda_enabled = cuda_manager.is_cuda_enabled()
        self._load_model()
    
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
                    self.device = cuda_manager.get_device()  # Это будет CPU
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
            
            # Транскрибируем аудио на указанном устройстве
            result = self.model.transcribe(voice_file_path, language="ru")
            transcribed_text = result["text"].strip()
            
            logger.info(f"✅ Транскрипция завершена. Длина текста: {len(transcribed_text)} символов")
            logger.debug(f"Транскрибированный текст: {transcribed_text[:100]}...")
            
            return transcribed_text
            
        except Exception as e:
            logger.error(f"❌ Ошибка транскрипции: {e}")
            raise
    
    async def download_and_transcribe(self, update: Update, context) -> str:
        """
        Скачивает голосовое сообщение и транскрибирует его
        
        Args:
            update: Объект Update от Telegram
            context: Контекст бота
            
        Returns:
            str: Транскрибированный текст
        """
        voice = update.message.voice
        
        try:
            # Скачиваем файл голосового сообщения
            logger.info("Скачиваю голосовое сообщение...")
            file = await context.bot.get_file(voice.file_id)
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
                temp_path = temp_file.name
            
            # Скачиваем файл во временную папку
            await file.download_to_drive(temp_path)
            logger.info(f"Файл скачан: {temp_path}")
            
            # Транскрибируем
            transcribed_text = await self.transcribe_voice_message(temp_path)
            
            # Удаляем временный файл
            try:
                os.unlink(temp_path)
                logger.info("Временный файл удален")
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл: {e}")
            
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Ошибка при скачивании и транскрипции: {e}")
            # Пытаемся удалить временный файл в случае ошибки
            try:
                if 'temp_path' in locals():
                    os.unlink(temp_path)
            except:
                pass
            raise

    def get_device_info(self):
        """Возвращает информацию об используемом устройстве"""
        return {
            "device": str(self.device),
            "device_name": self.device_name,
            "is_cuda_enabled": self.is_cuda_enabled,
            "model_size": self.model_size
        }

# Глобальный экземпляр транскриптора
transcriber = WhisperTranscriber(model_size="base")
