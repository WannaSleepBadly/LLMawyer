from telegram import Update
from telegram.ext import ContextTypes


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /status - показывает информацию о системе"""

    transcriber = context.bot_data["transcriber"]
    agent = context.bot_data["agent"]

    transcriber_info = transcriber.get_device_info()
    agent_info = agent.get_info()

    # Формируем сообщение
    status_message = "📊 **Статус системы:**\n\n"

    # Информация об устройстве
    device_emoji = "🚀" if transcriber_info["device"] == "cuda" else "💻"
    status_message += f"{device_emoji} **Устройство:** {transcriber_info['device']}\n"

    status_message += f"\n🤖 **Whisper модель:** {transcriber_info['model_size']}\n"
    status_message += f"\n⚖️ **Агент:** {agent_info['model']}\n"

    await update.message.reply_text(status_message, parse_mode="Markdown")
