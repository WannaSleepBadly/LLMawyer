import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    text = update.message.text

    # Логируем информацию о текстовом сообщении
    logger.info(
        f"Получено текстовое сообщение от {update.effective_user.username}: {text[:50]}..."
    )

    # Отправляем индикатор обработки
    processing_msg = await update.message.reply_text("⏳ Идёт обработка...")

    # Получаем ответ из ML модуля в отдельном потоке (CPU-bound / блокирующие вызовы)
    text_processor = context.bot_data["text_processor"]
    response = await asyncio.to_thread(text_processor.generate_response, text)

    # Удаляем сообщение об обработке и отправляем ответ
    await processing_msg.delete()
    await update.message.reply_text(
        response,
        parse_mode="HTML",
    )
