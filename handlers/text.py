import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from ML.responses import get_text_response

logger = logging.getLogger(__name__)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    text = update.message.text
    
    # Логируем информацию о текстовом сообщении
    logger.info(f"Получено текстовое сообщение от {update.effective_user.username}: {text[:50]}...")
    
    # Отправляем индикатор обработки
    processing_msg = await update.message.reply_text("⏳ Идёт обработка...")
    
    # Имитируем обработку (небольшая задержка)
    await asyncio.sleep(1.5)
    
    # Получаем случайный ответ из ML модуля
    response = get_text_response()
    
    # Удаляем сообщение об обработке и отправляем ответ
    await processing_msg.delete()
    await update.message.reply_text(response)
