from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("📋 Меню команд", callback_data='menu')],
        [InlineKeyboardButton("❓ Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Привет! Я универсальный бот-помощник!\n\n"
        "🎤 Принимаю голосовые сообщения\n"
        "💬 Обрабатываю текстовые сообщения\n"
        "⚡ Быстро отвечаю заглушками\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )
