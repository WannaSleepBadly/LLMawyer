from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'menu':
        keyboard = [
            [InlineKeyboardButton("🎤 Отправить голосовое", callback_data='voice_info')],
            [InlineKeyboardButton("💬 Отправить текст", callback_data='text_info')],
            [InlineKeyboardButton("❓ Помощь", callback_data='help')],
            [InlineKeyboardButton("🔙 Главное меню", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📋 Меню команд:\n\n"
            "🎤 Голосовые сообщения\n"
            "• Отправьте голосовое сообщение\n"
            "• Получите текстовый ответ-заглушку\n\n"
            "💬 Текстовые сообщения\n"
            "• Отправьте любой текст\n"
            "• Получите обработанный ответ\n\n"
            "⚡ Все сообщения обрабатываются с индикатором прогресса",
            reply_markup=reply_markup
        )
    
    elif query.data == 'help':
        keyboard = [
            [InlineKeyboardButton("📋 Меню команд", callback_data='menu')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📚 Справка по боту:\n\n"
            "🎤 Голосовые сообщения - отправьте голосовое сообщение, и я отвечу текстом\n"
            "💬 Текстовые сообщения - отправьте любой текст, и я обработаю его\n"
            "⚡ Все сообщения обрабатываются с индикатором 'идёт обработка'\n\n"
            "Доступные команды:\n"
            "• /start - начать работу с ботом\n"
            "• /help - показать эту справку\n"
            "• /menu - показать меню команд",
            reply_markup=reply_markup
        )
    
    elif query.data == 'voice_info':
        await query.edit_message_text(
            "🎤 Голосовые сообщения:\n\n"
            "Просто отправьте голосовое сообщение, и я:\n"
            "1. Покажу 'идёт обработка'\n"
            "2. Отвечу текстовой заглушкой\n\n"
            "Попробуйте прямо сейчас!"
        )
    
    elif query.data == 'text_info':
        await query.edit_message_text(
            "💬 Текстовые сообщения:\n\n"
            "Отправьте любой текст, и я:\n"
            "1. Покажу 'идёт обработка'\n"
            "2. Отвечу обработанной заглушкой\n\n"
            "Попробуйте прямо сейчас!"
        )
    
    elif query.data == 'back':
        keyboard = [
            [InlineKeyboardButton("📋 Меню команд", callback_data='menu')],
            [InlineKeyboardButton("❓ Помощь", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👋 Привет! Я универсальный бот-помощник!\n\n"
            "🎤 Принимаю голосовые сообщения\n"
            "💬 Обрабатываю текстовые сообщения\n"
            "⚡ Быстро отвечаю заглушками\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )
