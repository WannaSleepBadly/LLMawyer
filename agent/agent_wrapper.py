import logging
import os
import re
from typing import Dict, List, Optional

from LLMawyer.agent.graph import create_agent_graph
from LLMawyer.agent.setup.logging_setup import setup_langfuse
from LLMawyer.law_data.config import get_db_manager
from LLMawyer.law_data.models import Law, LawChapter, LawParagraph, LawPart

"""
Взаимодействие с агентом
"""

logger = logging.getLogger(__name__)


class AgentWrapper:
    """Обертка для агента, обеспечивающая форматирование ответов с метаданными."""

    def __init__(self):
        """Инициализация агента."""
        self.agent = create_agent_graph()
        self.db_manager = get_db_manager()
        self.langfuse, self.langfuse_handler = setup_langfuse()

    def generate_response(self, text: str) -> str:
        """
        Главная функция получения и форматирования ответа на текстовый вопрос

        Args:
            text (str): Текст вопроса пользователя

        Returns:
            str: Сгенерированный ответ с форматированием и ссылками на источники
        """
        try:
            logger.info(f"Обрабатываем текст: {text[:50]}")

            # Вызываем агента
            initial_state = {
                "question": text,
                "context": "",
                "answer": "",
                "retrieved_docs": [],
                "route": "",
            }

            result = self.agent.invoke(
                initial_state, {"callbacks": [self.langfuse_handler]}
            )

            answer = result.get("answer", "")
            if not answer:
                answer = "Извините, не удалось сформировать ответ на ваш вопрос."

            self.langfuse.flush()

            # Получаем метаданные документов для форматирования
            retrieved_docs = result.get("retrieved_docs", [])

            # Форматируем ответ с ссылками на источники
            formatted_response = self.format_response(answer, retrieved_docs)

            logger.info(f"Сформулирован ответ: {formatted_response[:100]}...")
            return formatted_response

        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}", exc_info=True)
            return "Ваш вопрос слишком сложный, я не могу на него ответить. Попробуйте перефразировать."

    def format_response(self, answer: str, retrieved_docs: List) -> str:
        """
        Форматирует ответ агента для пользователя.
        Добавляет внизу ссылки на использованные фрагменты законов.

        Args:
            answer: Ответ агента
            retrieved_docs: Список документов с метаданными

        Returns:
            str: Отформатированный ответ с ссылками
        """
        references = []

        # Получаем метаданные для документов
        for doc in retrieved_docs[:3]:  # Берем только первые 3
            metadata = doc.metadata
            paragraph_id = metadata.get("paragraph_id")

            if paragraph_id:
                details = self._get_paragraph_details(paragraph_id)
                if details:
                    ref = self._format_reference(details)
                    references.append(ref)

        # Ограничиваем длину ответа
        if len(answer) > 4000:
            answer = answer[:2500] + "..."

        # Конвертируем markdown в HTML
        answer = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", answer)
        answer = re.sub(r"\*(.+?)\*", r"<i>\1</i>", answer)

        # Добавляем ссылки на источники
        if references:
            references_text = "\n".join(references)
            formatted_answer = (
                f"{answer.strip()}\n\n<i>Источники:</i>\n{references_text}"
            )
        else:
            formatted_answer = answer.strip()

        return formatted_answer

    def _get_paragraph_details(self, paragraph_id: int) -> Optional[Dict]:
        """Получение информации о пунктах из PostgreSQL."""
        try:
            session = self.db_manager.get_session()

            paragraph = (
                session.query(LawParagraph)
                .join(LawPart, LawParagraph.part_id == LawPart.part_id)
                .join(LawChapter, LawPart.chapter_id == LawChapter.chapter_id)
                .join(Law, LawChapter.law_id == Law.law_id)
                .filter(LawParagraph.paragraph_id == paragraph_id)
                .first()
            )

            if not paragraph:
                session.close()
                return None

            details = {
                "paragraph_id": paragraph.paragraph_id,
                "content": paragraph.content,
                "paragraph_number": paragraph.number,
                "part": {
                    "part_id": paragraph.part.part_id,
                    "number": paragraph.part.number,
                    "title": paragraph.part.title,
                    "source_url": paragraph.part.source_url,
                },
                "chapter": {
                    "chapter_id": paragraph.part.chapter.chapter_id,
                    "number": paragraph.part.chapter.number,
                    "title": paragraph.part.chapter.title,
                    "source_url": paragraph.part.chapter.source_url,
                },
                "law": {
                    "law_id": paragraph.part.chapter.law.law_id,
                    "code": paragraph.part.chapter.law.code,
                    "name": paragraph.part.chapter.law.name,
                    "source_url": paragraph.part.chapter.law.source_url,
                },
            }

            session.close()
            return details

        except Exception as e:
            logger.error(f"Ошибка получения деталей пункта {paragraph_id}: {e}")
            return None

    @staticmethod
    def _format_reference(details: Dict) -> str:
        """Форматирование ссылки на источник."""
        return (
            f"{details['law']['name']} "
            f"<a href=\"{details['law']['source_url']}\">{details['law']['code']}</a> "
            f"<a href=\"{details['chapter']['source_url']}\">{details['chapter']['title']}</a> "
            f"<a href=\"{details['part']['source_url']}\">{details['part']['title']}</a> "
            f"Пункт {details['paragraph_number']}."
        )

    def get_info(self):
        return {"model": os.getenv("OLLAMA_MODEL")}
