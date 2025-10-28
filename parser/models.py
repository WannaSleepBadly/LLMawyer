import os
from typing import List, Optional#, Text
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, text, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import SQLAlchemyError

"""
Модуль для работы с PostgreSQL базой данных.
Содержит модели, подключение и репозиторий для работы с законами.
Структура: закон -> глава -> часть (статья) -> пункт
"""

# Базовый класс для моделей
Base = declarative_base()

class Law(Base):
    """Модель закона"""
    __tablename__ = 'laws'
    
    law_id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False)  # Название закона
    code = Column(String(50), nullable=False)  # Номер ФЗ
    source_url = Column(String(1000), nullable=False)  # Ссылка на источник
    created_at = Column(DateTime, default=datetime.utcnow)  # Дата загрузки
    
    # Связи
    chapters = relationship("LawChapter", back_populates="law", cascade="all, delete-orphan")


class LawChapter(Base):
    """Модель главы закона"""
    __tablename__ = 'chapters'
    
    chapter_id = Column(Integer, primary_key=True)
    law_id = Column(Integer, ForeignKey('laws.law_id'), nullable=False)
    number = Column(Integer, nullable=False)  # Номер главы
    title = Column(String(500), nullable=False)  # Название главы
    source_url = Column(String(1000), nullable=False)  # Ссылка на источник

    # Связи
    law = relationship("Law", back_populates="chapters")
    parts = relationship("LawPart", back_populates="chapter", cascade="all, delete-orphan")


class LawPart(Base):
    """Модель части/статьи закона"""
    __tablename__ = 'parts'
    
    part_id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer, ForeignKey('chapters.chapter_id'), nullable=False)
    number = Column(String(50), nullable=False)  # Номер части/статьи
    title = Column(String(500), nullable=False)  # Название части/статьи
    source_url = Column(String(1000), nullable=False)  # Ссылка на источник

    # Связи
    chapter = relationship("LawChapter", back_populates="parts")
    paragraphs = relationship("LawParagraph", back_populates="part", cascade="all, delete-orphan")


class LawParagraph(Base):
    """Модель пункта закона"""
    __tablename__ = 'paragraphs'
    
    paragraph_id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey('parts.part_id'), nullable=False)
    number = Column(String(50), nullable=False)  # Номер пункта
    content = Column(Text, nullable=False)  # Исходный текст пункта

    # Связи
    part = relationship("LawPart", back_populates="paragraphs")


class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    def __init__(self, database_url: str):
        """
        Инициализация подключения к базе данных
        
        Args:
            database_url: URL подключения к PostgreSQL Пример: postgresql://user:password@localhost:5432/dbname
        """
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Создание всех таблиц в базе данных"""
        try:
            Base.metadata.create_all(bind=self.engine)
            print("✅ Таблицы созданы успешно")
        except SQLAlchemyError as e:
            print(f"❌ Ошибка создания таблиц: {e}")
            raise
    
    def get_session(self) -> Session:
        """Получение сессии базы данных"""
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """Тестирование подключения к базе данных"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                print("✅ Подключение к базе данных успешно")
                return True
        except SQLAlchemyError as e:
            print(f"❌ Ошибка подключения к базе данных: {e}")
            return False


class LawRepository:
    """Репозиторий для работы с данными законов"""
    
    def __init__(self, session: Session):
        self.session = session
    
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
    
    def search_in_content(self, search_term: str, law_code: str = None) -> List[LawParagraph]:
        """Поиск по содержимому пунктов"""
        query = self.session.query(LawParagraph).filter(
            LawParagraph.content.contains(search_term)
        )
        
        if law_code:
            query = query.join(Law).filter(Law.law_code == law_code)
        
        return query.all()


# Глобальные переменные для подключения
from .config import DatabaseConfig

db_config = DatabaseConfig()
DATABASE_URL = db_config.get_database_url()
# Создаем менеджер базы данных
db_manager = DatabaseManager(DATABASE_URL)
engine = db_manager.engine
SessionLocal = db_manager.SessionLocal
db_manager.create_tables()
