"""
Пакет для парсинга законов и работы с базой данных PostgreSQL.

Модули:
- law_parser: Основной парсер закона "О рекламе"
- database: Модели и подключение к PostgreSQL
- config: Конфигурация базы данных
- test_database: Тесты для проверки работы с БД
- setup: Скрипт настройки окружения
"""

from .law_parser import LAW_CODE, LAW_NAME, LAW_BASE_URL
from .models import (
    Base, Law, LawChapter, LawPart, LawParagraph,
    DatabaseManager, LawRepository, SessionLocal, engine
)
from .config import DatabaseConfig, setup_database

__all__ = [
    # Основные функции
    'setup_database',
    
    # Константы
    'LAW_CODE',
    'LAW_NAME', 
    'LAW_BASE_URL',
    
    # Модели базы данных
    'Base',
    'Law',
    'LawChapter',
    'LawPart',
    'LawParagraph',
    
    # Управление базой данных
    'DatabaseManager',
    'LawRepository',
    'SessionLocal',
    'engine',
    
    # Конфигурация
    'DatabaseConfig'
]
