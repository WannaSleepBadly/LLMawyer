import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик голосовых сообщений с транскрипцией Whisper"""
    voice = update.message.voice
    transcriber = context.bot_data["transcriber"]
    agent = context.bot_data["agent"]

    # Логируем информацию о голосовом сообщении
    logger.info(f"Получено голосовое сообщение от {update.effective_user.username}")
    logger.info(
        f"Длительность: {voice.duration} сек, размер файла: {voice.file_size} байт"
    )

    # Отправляем индикатор обработки
    processing_msg = await update.message.reply_text("⏳ Идёт обработка...")

    try:
        # Имитируем обработку (небольшая задержка)
        await asyncio.sleep(1.0)

        # Обновляем сообщение о прогрессе
        await processing_msg.edit_text("🎤 Транскрибирую голосовое сообщение...")

        # Транскрибируем голосовое сообщение
        transcribed_text = await transcriber.download_and_transcribe(update, context)

        # Обновляем сообщение о прогрессе
        await processing_msg.edit_text("🤖 Анализирую правовую базу...")

        # Генерируем ответ на основе транскрипции
        response = agent.generate_response(transcribed_text)

        # Удаляем сообщение об обработке и отправляем ответ
        await processing_msg.delete()
        await update.message.reply_text(response, parse_mode="HTML")

        logger.info(
            f"Успешно обработано голосовое сообщение. Транскрипция: {transcribed_text[:50]}..."
        )

    except Exception as e:
        logger.error(f"Ошибка обработки голосового сообщения: {e}")

        # В случае ошибки отправляем заглушку
        await processing_msg.edit_text(
            "❌ Ошибка обработки. Отправляю стандартный ответ..."
        )
        await asyncio.sleep(1.0)

        await processing_msg.delete()
        await update.message.reply_text("🎤 Голосовое сообщение получено!\n\n🤖")
