import os
from typing import List, Dict

from ollama import Client


class OllamaClient:
    def __init__(self):
        """
        Клиент для работы с Ollama
        """
        self.model = os.getenv('OLLAMA_MODEL')
        self.client = Client()

    def create_chat_completion(self, messages: List[Dict[str, str]]):

        response = self.client.chat(self.model, messages=messages, stream=True)
        result = ""
        for part in response:
            result += part['message']['content']
        return result

    def get_answer(self, user_question, paragraphs):
        system_message = {
            "role": "system",
            "content": (
                "Вы — юридический ассистент, который отвечает на вопросы по российскому законодательству. "
                "Дайте простой ответ на вопрос пользователя, используя только приведённые статьи."
            )
        }

        context_text = "\n\n".join(paragraphs)
        user_message = {
            "role": "user",
            "content": f"Вопрос: {user_question}\n\nСтатьи, отвечающие на вопрос:\n{context_text}"
        }

        messages = [system_message, user_message]

        result = self.create_chat_completion(messages)
        return result


ollama_client = OllamaClient()
