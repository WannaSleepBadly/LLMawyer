import logging
from rag.rag_search import get_rag_service
import re
from .llm_api import ollama_client

logger = logging.getLogger(__name__)
rag_service = get_rag_service()


class TextProcessor:
    """Класс для обработки текстовых(транскрибированных) сообщений"""

    def generate_response(self, text: str) -> str:
        """
        Главная функция формирования ответа на текстовый вопрос.
        
        Args:
            text (str): Текст вопроса пользователя
            
        Returns:
            str: Сгенерированный ответ
        """
        try:
            logger.info(f"Обрабатываем текст: {text[:50]}")

            # Используем ленивую инициализацию RAG один раз на процесс
            retrieved_fragments = rag_service.search_similar_paragraphs(text, top_k=5)

            paragraphs = [fragment['content'] for fragment in retrieved_fragments]
            llm_answer = ollama_client.get_answer(text, paragraphs)
            logger.info(llm_answer)
            response = self.format_response(llm_answer, retrieved_fragments)

            logger.info(f"Сформулирован ответ: {response}")
            return response

        except Exception as e:
            logger.error(f"❌ Ошибка генерации ответа: {e}")
            return "Ваш вопрос слишком сложный, я не могу на него ответить. Попробуйте перефразировать."

    def format_response(self, llm_answer: str, retrieved_fragments: list[dict[str, any]]) -> str:
        """
        Форматирует ответ LLM для пользователя.
        Добавляет внизу ссылки на использованные фрагменты законов.
        """
        references = []
        retrieved_fragments = retrieved_fragments[:3]
        for i, frag in enumerate(retrieved_fragments, 1):
            ref = (
                f"""{i}. <a href="{frag['law_url']}"> {frag['law_name']}</a> <a href="{frag['chapter_url']}"> {frag['chapter_title']}</a> <a href="{frag['part_url']}"> {frag['part_title']}</a> Пункт {frag['paragraph_number']}."""
                )
            references.append(ref)

        if len(llm_answer) > 4000:  # ограничение Telegram
            llm_answer = llm_answer[:2500]

        # Сначала обрабатываем жирный (**...**)
        llm_answer = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', llm_answer)
        # Курсив (*...*)
        llm_answer = re.sub(r'\*(.+?)\*', r'<i>\1</i>', llm_answer)

        references_text = "\n".join(references)
        formatted_answer = f"{llm_answer.strip()}\n\n<i>Источники:</i>\n{references_text}"

        return formatted_answer


# Глобальный экземпляр процессора текста
text_processor = TextProcessor()
