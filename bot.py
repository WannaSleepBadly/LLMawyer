import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv

# Импорты из модулей
from commands import start_command, menu_command, status_command
from handlers import handle_voice, handle_text, handle_other, button_callback

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Основная функция для запуска бота"""
    # Получаем токен бота из переменных окружения
    token = os.getenv('BOT_TOKEN')
    
    if not token:
        logger.error("Не найден BOT_TOKEN в переменных окружения!")
        return
    
    # Создаем приложение
    application = Application.builder().token(token).build()
    
    # Добавляем обработчики
    #Обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    # Вызов обработчика для голосовых сообщений
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    # Вызов обработчика для текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    # Вызов обработчика для всех остальных сообщений
    application.add_handler(MessageHandler(filters.ALL, handle_other))
    
    # Запускаем бота
    logger.info("Запускаю бота...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
