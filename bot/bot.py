import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from LLMawyer.agent.agent_wrapper import AgentWrapper
from LLMawyer.bot.commands.start import start_command
from LLMawyer.bot.commands.status import status_command
from LLMawyer.bot.handlers.other import handle_other
from LLMawyer.bot.handlers.text import handle_text
from LLMawyer.bot.handlers.voice import handle_voice
from LLMawyer.stt.transcriber import Transcriber

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
        self.transcriber = None
        self.agent = None

    def init_services(self):
        """Инициализация всех вычислительных моделей и бэкендов."""
        logger.info("Загружаю сервисы...")

        self.transcriber = Transcriber()
        self.transcriber.load_model()
        logger.info("Whisper загружен")

        # Агент (включает RAG и LLM)
        self.agent = AgentWrapper()
        logger.info("Агент готов")

    def init_handlers(self):
        app = self.application

        # Команды
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("status", status_command))

        # Голос
        app.add_handler(MessageHandler(filters.VOICE, handle_voice))

        # Текст
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

        # Остальное
        app.add_handler(MessageHandler(filters.ALL, handle_other))

    async def on_bot_ready(self, app):
        app.bot_data["transcriber"] = self.transcriber
        app.bot_data["agent"] = self.agent

    def run(self):
        logger.info("Запуск Telegram-бота...")

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
