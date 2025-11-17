from telegram import Update
from telegram.ext import ContextTypes


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /status - показывает информацию о системе"""

    transcriber = context.bot_data["transcriber"]
    text_processor = context.bot_data["text_processor"]

    cuda_info = transcriber.cuda_manager.get_device_info()
    transcriber_info = transcriber.get_device_info()
    embedding_info = text_processor.rag_service.embedding_service.get_model_info()
    ollama_info = text_processor.ollama_client.get_info()

    # Формируем сообщение
    status_message = "📊 **Статус системы:**\n\n"

    # Информация об устройстве
    device_emoji = "🚀" if cuda_info["is_cuda"] else "💻"
    status_message += f"{device_emoji} **Устройство:** {cuda_info['name']}\n"

    if cuda_info["is_cuda"]:
        status_message += f"💾 **Память GPU:** {cuda_info['memory_gb']} GB\n"
        status_message += "✅ **CUDA:** Включена\n"
    else:
        status_message += "⚠️ **CUDA:** Недоступна\n"

    status_message += f"\n🤖 **Whisper модель:** {transcriber_info['model_size']}\n"
    status_message += f"\n🔎 **Embedding модель:** {embedding_info['model_name']}\n"
    status_message += f"\n ⚖️**LLM модель:** {ollama_info['model_name']}\n"

    await update.message.reply_text(status_message, parse_mode="Markdown")
