from .config import db_manager, db_config
from .models import Law, LawChapter, LawPart, LawParagraph
from .repository import LawRepository

"""
Модуль работы с Postgres
"""

__all__ = [
    'db_manager', 'db_config',
    'Law', 'LawChapter', 'LawPart', 'LawParagraph',
    'LawRepository'
]
