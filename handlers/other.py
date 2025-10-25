from telegram import Update
from telegram.ext import ContextTypes

async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик других типов сообщений"""
    await update.message.reply_text(
        "Я работаю с голосовыми и текстовыми сообщениями! 🎤💬\n"
        "Пожалуйста, отправьте голосовое сообщение или текст."
    )
