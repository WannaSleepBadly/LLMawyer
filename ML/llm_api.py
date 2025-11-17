import os
from typing import Dict, List

from ollama import Client

"""
Модуль обращения к Ollama для генерации ответа
"""


class OllamaClient:
    def __init__(self):
        """
        Клиент для работы с Ollama
        """
        self.model = os.getenv("OLLAMA_MODEL")
        self.client = Client()

    def create_chat_completion(self, messages: List[Dict[str, str]]):

        response = self.client.chat(self.model, messages=messages, stream=True)
        result = ""
        for part in response:
            result += part["message"]["content"]
        return result

    def get_answer(self, user_question, paragraphs):
        system_message = {
            "role": "system",
            "content": (
                """Ты — юридический консультант, специализирующийся на законодательстве Российской Федерации. Твоя
                задача — давать точные, аккуратные и нейтральные ответы на вопросы пользователей только на основе
                предоставленных фрагментов законодательства. Если информации в этих фрагментах недостаточно для
                уверенного ответа, дай общий ответ на вопрос пользователя и предположи, какие дополнительные нормы
                могли бы быть релевантны, не придумывая законы. Пиши понятным юридическим языком, избегай чрезмерно
                сложных формулировок."""
            ),
        }

        context_text = "\n\n".join(paragraphs)
        user_message = {
            "role": "user",
            "content": f"Вопрос: {user_question}\n\nСтатьи, отвечающие на вопрос:\n{context_text}",
        }

        messages = [system_message, user_message]

        result = self.create_chat_completion(messages)
        return result

    def get_info(self):
        return {"model_name": self.model}
