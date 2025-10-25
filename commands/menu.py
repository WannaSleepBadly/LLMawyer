from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /menu"""
    keyboard = [
        [InlineKeyboardButton("🎤 Отправить голосовое", callback_data='voice_info')],
        [InlineKeyboardButton("💬 Отправить текст", callback_data='text_info')],
        [InlineKeyboardButton("❓ Помощь", callback_data='help')],
        [InlineKeyboardButton("🔙 Главное меню", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📋 Меню команд:\n\n"
        "🎤 Голосовые сообщения\n"
        "• Отправьте голосовое сообщение\n"
        "• Получите транскрипцию с помощью Whisper\n"
        "• Получите умный ответ на основе содержания\n\n"
        "💬 Текстовые сообщения\n"
        "• Отправьте любой текст\n"
        "• Получите обработанный ответ\n\n"
        "⚡ Все сообщения обрабатываются с индикатором прогресса",
        reply_markup=reply_markup
    )
