from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("📋 Меню команд", callback_data='menu')],
        [InlineKeyboardButton("🎤 Отправить голосовое", callback_data='voice_info')],
        [InlineKeyboardButton("💬 Отправить текст", callback_data='text_info')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Привет! Я универсальный бот-помощник по законодательству Российской Федерации!\n\n"
        "🎤 Принимаю голосовые и текстовые сообщения\n"
        "⚡ Быстро разъясняю и анализирую нормативные акты\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )
