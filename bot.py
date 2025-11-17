import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from commands.start import start_command
from commands.status import status_command
from handlers.buttons import button_callback
from handlers.other import handle_other
from handlers.text import handle_text
from handlers.voice import handle_voice
from LLMawyer.ML.cuda_manager import CUDAManager
from LLMawyer.ML.llm_api import OllamaClient
from LLMawyer.ML.text_processor import TextProcessor
from LLMawyer.ML.whisper_transcriber import WhisperTranscriber
from LLMawyer.parser.config import get_db_manager
from LLMawyer.rag.embedding_service import EmbeddingService
from LLMawyer.rag.milvus_manager import MilvusManager
from LLMawyer.rag.rag_search import RAGSearchService

logger = logging.getLogger(__name__)


class BotApp:
    """Главный класс бота. Управляет инициализацией сервисов и запуском."""

    def __init__(self):
        load_dotenv()
        self.token = os.getenv("BOT_TOKEN")

        if not self.token:
            raise RuntimeError("BOT_TOKEN не найден в переменных окружения!")

        self.application: Application | None = None

        # Внутренние сервисы
        self.cuda_manager = None
        self.transcriber = None
        self.milvus_manager = None
        self.embedding_service = None
        self.db_manager = None
        self.rag_service = None
        self.ollama_client = None
        self.text_processor = None

    def init_services(self):
        """Инициализация всех вычислительных моделей и бэкендов."""
        logger.info("⚙ Загружаю сервисы...")

        self.cuda_manager = CUDAManager()

        # Whisper
        self.transcriber = WhisperTranscriber(self.cuda_manager)
        self.transcriber._load_model()
        logger.info("🎤 Whisper загружен")

        # RAG
        self.milvus_manager = MilvusManager()
        self.embedding_service = EmbeddingService()
        self.db_manager = get_db_manager()

        self.rag_service = RAGSearchService(
            self.milvus_manager, self.embedding_service, self.db_manager
        )

        if not self.rag_service.initialized:
            self.rag_service.initialize()
        logger.info("📚 RAG поисковый сервис инициализирован")

        # LLM
        self.ollama_client = OllamaClient()
        self.text_processor = TextProcessor(self.rag_service, self.ollama_client)
        logger.info("🤖 LLM и TextProcessor готовы")

    def init_handlers(self):
        app = self.application

        # Команды
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("status", status_command))

        # Кнопки
        app.add_handler(CallbackQueryHandler(button_callback))

        # Голос
        app.add_handler(MessageHandler(filters.VOICE, handle_voice))

        # Текст
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

        # Остальное
        app.add_handler(MessageHandler(filters.ALL, handle_other))

    async def on_bot_ready(self, app):
        app.bot_data["transcriber"] = self.transcriber
        app.bot_data["text_processor"] = self.text_processor

    def run(self):
        logger.info("🚀 Запуск Telegram-бота...")

        self.application = (
            Application.builder()
            .token(self.token)
            .read_timeout(100)
            .write_timeout(100)
            .post_init(self.on_bot_ready)
            .build()
        )

        # Загружаем модели
        self.init_services()

        # Подключаем обработчики
        self.init_handlers()

        # Старт
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    bot = BotApp()
    bot.run()


if __name__ == "__main__":
    main()
