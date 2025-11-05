from telegram import Update
from telegram.ext import ContextTypes
from commands.status import status_command


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    if query.data == 'status':
        await status_command(query, context)
    
    elif query.data == 'voice_info':
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Просто отправьте голосовое сообщение с вашим вопросом.\n"
            "Вопрос может быть общим или с указанием конкретных статьей и законов.\n"
            "Например, я могу рассказать, что должен знать рекламодатель, размещая рекламу в интернете\n"
            "Или описать простыми словами статью 18.2 Федерального закона 'О рекламе'\n"
            "Я распознаю речь и отвечу на вопросы о законодательстве."
        )
    
    elif query.data == 'text_info':
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Опишите вопрос о законодательстве. Вопрос может быть общим или с указанием конкретных статьей и "
                 "законов.\n"
            "Например, я могу рассказать, что должен знать рекламодатель, размещая рекламу в интернете\n"
            "Или описать простыми словами статью 18.2 Федерального закона 'О рекламе'"
        )

