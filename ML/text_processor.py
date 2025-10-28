import logging
import random
from typing import Optional
from rag.rag_search import get_rag_service

logger = logging.getLogger(__name__)
rag_service = get_rag_service()
class TextProcessor:
    """Класс для обработки транскрибированного текста"""
    
    
    def generate_response(self, text: str) -> str:
        """
        Главная функция формирования ответа на текстовый вопрос.
        
        Args:
            text (str): Текст вопроса пользователя
            
        Returns:
            str: Сгенерированный ответ
        """
        try:
            logger.info(f"✨ Обрабатываем текст: {text[:50]}")

            # Используем ленивую инициализацию RAG один раз на процесс
            #rag_service = get_rag_service()

            results = rag_service.search_similar_paragraphs(text, top_k=5)
            response = self.format_response(results)

            logger.info(f"✨ Найденные похожие пункты закона: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return "Ваш вопрос слишком сложный, я не могу на него ответить. Попробуйте перефразировать."

    def format_response(self, response: list[dict[str, any]]) -> str:
        """Форматирование ответа о похожих на запрос пользователя пунктов закона"""
        for_response = ""
        for paragraph in response:
            for_response += str(paragraph)
        return for_response

# Глобальный экземпляр процессора текста
text_processor = TextProcessor()
