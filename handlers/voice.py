import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from ML.responses import get_voice_response
from ML.whisper_transcriber import transcriber
from ML.text_processor import text_processor
from ML.cuda_manager import cuda_manager

logger = logging.getLogger(__name__)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик голосовых сообщений с транскрипцией Whisper"""
    voice = update.message.voice
    
    # Логируем информацию о голосовом сообщении
    logger.info(f"Получено голосовое сообщение от {update.effective_user.username}")
    logger.info(f"Длительность: {voice.duration} сек, размер файла: {voice.file_size} байт")
    
    # Отправляем индикатор обработки
    processing_msg = await update.message.reply_text("⏳ Идёт обработка...")
    
    try:
        # Имитируем обработку (небольшая задержка)
        await asyncio.sleep(1.0)
        
        # Получаем информацию об устройстве
        device_info = transcriber.get_device_info()
        device_emoji = "🚀" if device_info["is_cuda_enabled"] else "💻"
        
        # Обновляем сообщение о прогрессе
        await processing_msg.edit_text(f"🎤 Транскрибирую голосовое сообщение...\n{device_emoji} Устройство: {device_info['device_name']}")
        
        # Транскрибируем голосовое сообщение
        transcribed_text = await transcriber.download_and_transcribe(update, context)
        
        # Обновляем сообщение о прогрессе
        await processing_msg.edit_text("🤖 Анализирую текст и формирую ответ...")
        
        # Генерируем ответ на основе транскрипции
        response = text_processor.generate_response(transcribed_text)
        
        # Форматируем финальный ответ
        final_response = text_processor.format_transcription_response(transcribed_text, response)
        
        # Удаляем сообщение об обработке и отправляем ответ
        await processing_msg.delete()
        await update.message.reply_text(final_response, parse_mode='Markdown')
        
        logger.info(f"Успешно обработано голосовое сообщение. Транскрипция: {transcribed_text[:50]}...")
        
    except Exception as e:
        logger.error(f"Ошибка обработки голосового сообщения: {e}")
        
        # В случае ошибки отправляем заглушку
        await processing_msg.edit_text("❌ Ошибка обработки. Отправляю стандартный ответ...")
        await asyncio.sleep(1.0)
        
        fallback_response = get_voice_response()
        await processing_msg.delete()
        await update.message.reply_text(f"🎤 Голосовое сообщение получено!\n\n🤖 {fallback_response}")
