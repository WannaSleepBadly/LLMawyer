from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    keyboard = [
        [InlineKeyboardButton("📋 Меню команд", callback_data='menu')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📚 Справка по боту:\n\n"
        "🎤 Голосовые сообщения - отправьте голосовое сообщение, и я транскрибирую его с помощью Whisper и отвечу умным ответом\n"
        "💬 Текстовые сообщения - отправьте любой текст, и я обработаю его\n"
        "⚡ Все сообщения обрабатываются с индикатором 'идёт обработка'\n\n"
        "Доступные команды:\n"
        "• /start - начать работу с ботом\n"
        "• /help - показать эту справку\n"
        "• /menu - показать меню команд\n"
        "• /status - показать статус системы и CUDA",
        reply_markup=reply_markup
    )
