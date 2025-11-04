from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


"""
Модели таблиц в PostgreSQL базе данных.
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
    number = Column(String(50), nullable=False)  # Номер главы, "2", "2.1" или "II"
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
    number = Column(String(50), nullable=False)  # Номер пункта с подпунктом, если имеется
    content = Column(Text, nullable=False)  # Исходный текст пункта

    # Связи
    part = relationship("LawPart", back_populates="paragraphs")

