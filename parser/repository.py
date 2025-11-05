from typing import List, Optional, Type
import json
import re

from .models import *
from .config import db_manager

"""
CRUD операции с PostgreSQL таблицами законов
"""


class LawRepository:
    """Репозиторий для работы с данными законов"""

    def __init__(self):
        self.session = db_manager.get_session()

    def create_law(self, law_name: str, law_code: str, source_url: str) -> Law:
        """Создание нового закона"""
        law = Law(
            name=law_name,
            code=law_code,
            source_url=source_url
        )
        print('⚠️', law)
        self.session.add(law)
        self.session.flush()  # Получаем ID без коммита
        return law

    def create_chapter(self, law_id: int, chapter_number: int, title: str, source_url: str) -> LawChapter:
        """Создание главы закона"""
        chapter = LawChapter(
            law_id=law_id,
            number=chapter_number,
            title=title,
            source_url=source_url
        )
        self.session.add(chapter)
        self.session.flush()  # Получаем ID без коммита
        return chapter

    def create_part(self, chapter_id: int, part_number: str, title: str, source_url: str) -> LawPart:
        """Создание части/статьи закона"""
        part = LawPart(
            chapter_id=chapter_id,
            number=part_number,
            title=title,
            source_url=source_url
        )
        self.session.add(part)
        self.session.flush()  # Получаем ID без коммита
        return part

    def create_paragraph(self, part_id: int, paragraph_number: str, content: str) -> LawParagraph:
        """Создание пункта закона"""
        paragraph = LawParagraph(
            part_id=part_id,
            number=paragraph_number,
            content=content
        )
        self.session.add(paragraph)
        return paragraph

    def bulk_commit(self):
        """Массовый коммит изменений"""
        self.session.commit()

    def get_law_by_code(self, law_code: str) -> Optional[Law]:
        """Получение закона по коду"""
        return self.session.query(Law).filter(
            Law.code == law_code
        ).first()

    def get_chapters_by_law(self, law_id: int) -> List[LawChapter]:
        """Получение всех глав закона"""
        return self.session.query(LawChapter).filter(
            LawChapter.law_id == law_id
        ).order_by(LawChapter.number).all()

    def get_parts_by_chapter(self, chapter_id: int) -> List[LawPart]:
        """Получение всех частей главы"""
        return self.session.query(LawPart).filter(
            LawPart.chapter_id == chapter_id
        ).order_by(LawPart.part_number).all()

    def get_paragraphs_by_part(self, part_id: int) -> List[LawParagraph]:
        """Получение всех пунктов части"""
        return self.session.query(LawParagraph).filter(
            LawParagraph.part_id == part_id
        ).order_by(LawParagraph.paragraph_number).all()

    def search_in_content(self, search_term: str, law_code: str = None) -> list[Type[LawParagraph]]:
        """Поиск по содержимому пунктов"""
        query = self.session.query(LawParagraph).filter(
            LawParagraph.content.contains(search_term)
        )

        if law_code:
            query = query.join(Law).filter(Law.law_code == law_code)

        return query.all()

    @staticmethod
    def _get_number(title):
        pattern = r'(?:Статья|Глава)\s+(\d+(?:\.\d+)?)'
        match = re.search(pattern, title)

        return match.group(1) if match else "0"

    @staticmethod
    def _shorten_title(title):
        if len(title) > 500:
            title = title[:496] + '...'
        return title

    def save_law_to_database(self, law_data) -> None:
        """Сохранение спарсенных данных в БД со структурой: закон -> глава -> часть -> пункт"""

        print('Начали сохранять структуру')
        try:
            code = law_data["code"]
            # Проверяем, существует ли уже закон
            existing_law = self.get_law_by_code(code)
            if existing_law:
                print(f"⚠️ Закон {code} уже существует в БД. Перезаписать данные? y/n")
                answer = input()
                if answer == "y":
                    self.session.delete(existing_law)
                    self.session.commit()
                else:
                    return

            # Создаем новый закон
            law = self.create_law(
                law_name=law_data["title"],
                law_code=code,
                source_url=law_data["source_url"]
            )

            print(f"✅ Создан закон ID={law.law_id}: {law.name}")

            # Сохранение по структуре: глава → части → пункты
            total_count = 0  # Количество созданных записей
            for chapter_data in law_data['chapters']:
                # Сохраняем главу
                print(f"[Глава]: {chapter_data['title']}")
                try:
                    chapter_num = self._get_number(chapter_data["title"])

                    chapter = self.create_chapter(
                        law_id=law.law_id,
                        chapter_number=chapter_num,
                        title=self._shorten_title(chapter_data["title"]),
                        source_url=chapter_data["source_url"]
                    )
                    total_count += 1

                except Exception as e:
                    print(f"  ⚠️ Ошибка сохранения главы: {e}")

                # Парсим статьи этой главы
                for article_data in chapter_data["articles"]:
                    print(f"  [Статья]: {article_data['title']}")

                    try:
                        part_num = self._get_number(article_data["title"])

                        part = self.create_part(
                            chapter_id=chapter.chapter_id,
                            part_number=part_num,
                            title=self._shorten_title(article_data["title"]),
                            source_url=article_data["source_url"]
                        )
                        total_count += 1

                        for paragraph_data in article_data['paragraphs']:
                            paragraph = self.create_paragraph(
                                part_id=part.part_id,
                                paragraph_number=paragraph_data["number"],
                                content=paragraph_data["content"]
                            )
                            total_count += 1

                        # Коммитим каждые 10 записей
                        if total_count % 10 == 0:
                            self.session.commit()

                    except Exception as e:
                        print(f"    ⚠️ Ошибка сохранения части: {e}")
                        continue

            self.session.commit()
            print(f"✅ Сохранено {total_count} записей в БД")

        except Exception as e:
            self.session.rollback()
            print(f"❌ Ошибка сохранения в БД: {e}")
            raise
        finally:
            self.session.close()


if __name__ == "__main__":
    law_repository = LawRepository()
    with open('laws.json', 'r', encoding='utf-8') as file:
        laws = json.load(file)
    for law in laws:
        law_repository.save_law_to_database(law)
