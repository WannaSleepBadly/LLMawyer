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
            [InlineKeyboardButton("🔙 Главное меню", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
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
    
    elif query.data == 'voice_info':
        await query.edit_message_text(
            "Просто отправьте голосовое сообщение с вашим вопросом.\n"
            "Вопрос может быть общим или с указанием конкретных статьей и законов.\n"
            "Например, я могу рассказать, что должен знать рекламодатель, размещая рекламу в интернете\n"
            "Или описать простыми словами статью 18.2 Федерального закона 'О рекламе'\n"
            "Я распознаю речь и отвечу на вопросы о законодательстве."
        )
    
    elif query.data == 'text_info':
        await query.edit_message_text(
            "Опишите вопрос о законодательстве. Вопрос может быть общим или с указанием конкретных статьей и законов.\n"
            "Например, я могу рассказать, что должен знать рекламодатель, размещая рекламу в интернете\n"
            "Или описать простыми словами статью 18.2 Федерального закона 'О рекламе'"
        )
    
    elif query.data == 'back':
        keyboard = [
            [InlineKeyboardButton("📋 Меню команд", callback_data='menu')],
            [InlineKeyboardButton("🎤 Отправить голосовое", callback_data='voice_info')],
            [InlineKeyboardButton("💬 Отправить текст", callback_data='text_info')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👋 Привет! Я универсальный бот-помощник по законодательству Российской Федерации!\n\n"
            "🎤 Принимаю голосовые и текстовые сообщения\n"
            "⚡ Быстро разъясняю и анализирую нормативные акты\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )
