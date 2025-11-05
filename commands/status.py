from telegram import Update
from telegram.ext import ContextTypes
from ML.cuda_manager import cuda_manager
from ML.whisper_transcriber import get_transcriber
from ML.llm_api import ollama_client
from rag.rag_search import get_rag_service


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /status - показывает информацию о системе"""
    
    # Получаем информацию о CUDA
    cuda_info = cuda_manager.get_device_info()
    transcriber = get_transcriber()
    rag_search = get_rag_service()
    # Получаем информацию о транскрипторе
    transcriber_info = transcriber.get_device_info()
    embedding_info = rag_search.embedding_service.get_model_info()
    ollama_info = ollama_client.get_info()
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
    
    await update.message.reply_text(status_message, parse_mode='Markdown')
