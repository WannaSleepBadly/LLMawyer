from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /menu"""
    keyboard = [
        [InlineKeyboardButton("🎤 Отправить голосовое", callback_data='voice_info')],
        [InlineKeyboardButton("💬 Отправить текст", callback_data='text_info')],
        [InlineKeyboardButton("🔙 Главное меню", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📚 Справка по боту:\n\n"
        "Бот принимает голосовые и текстовые сообщения и отвечает на вопросы о законодательстве."
        "При указании конкретных статьей и законов, ответ будет более точным.\n"
        "Просто отправьте голосовое или текстовое сообщение и получите ответ.\n\n"
        "Доступные команды:\n"
        "• /start - начать работу с ботом\n"
        "• /menu - показать меню команд\n"
        "• /status - показать статус системы и CUDA",
        reply_markup=reply_markup
    )
