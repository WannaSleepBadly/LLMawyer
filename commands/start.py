from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

# TODO добавить команду /punct с указанием конкретного пункта закона
# TODO добавить команду /explain с объяснением, что регулирует конкретный ФЗ, на какие вопросы отвечает


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("🎤 Отправить голосовое", callback_data="voice_info")],
        [InlineKeyboardButton("💬 Отправить текст", callback_data="text_info")],
        [InlineKeyboardButton("📊 Статус системы", callback_data="status")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Привет! Я универсальный бот-помощник по законодательству Российской Федерации!\n\n"
        "🎤 Принимаю голосовые и текстовые сообщения\n"
        "Доступные законы для анализа:\n"
        "* Федеральный закон О рекламе от 13.03.2006 N 38-ФЗ (последняя редакция)\n"
        "* Закон РФ О защите прав потребителей (ЗОЗПП) от 07.02.1992 N 2300-1 (последняя редакция)\n"
        "* Федеральный закон О защите конкуренции от 26.07.2006 N 135-ФЗ (последняя редакция)\n"
        "* Федеральный закон Об информации, информационных технологиях и о защите информации от 27.07.2006 N 149-ФЗ ("
        "последняя редакция)\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
    )
