import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from ML.responses import get_voice_response

logger = logging.getLogger(__name__)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик голосовых сообщений"""
    voice = update.message.voice
    
    # Логируем информацию о голосовом сообщении
    logger.info(f"Получено голосовое сообщение от {update.effective_user.username}")
    logger.info(f"Длительность: {voice.duration} сек, размер файла: {voice.file_size} байт")
    
    # Отправляем индикатор обработки
    processing_msg = await update.message.reply_text("⏳ Идёт обработка...")
    
    # Имитируем обработку (небольшая задержка)
    await asyncio.sleep(1.5)
    
    # Получаем случайный ответ из ML модуля
    response = get_voice_response()
    
    # Удаляем сообщение об обработке и отправляем ответ
    await processing_msg.delete()
    await update.message.reply_text(response)
