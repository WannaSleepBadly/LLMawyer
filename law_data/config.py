import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from .models import Base

"""
Конфигурация для подключения к PostgreSQL.
"""

load_dotenv()


class DatabaseConfig:
    """Конфигурация базы данных"""

    # Параметры подключения к PostgreSQL
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "llmawyer")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

    @classmethod
    def get_database_url(cls) -> str:
        """Получение URL подключения к базе данных"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"


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
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

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


def get_db_manager():
    db_config = DatabaseConfig()
    DATABASE_URL = db_config.get_database_url()
    # Создаем менеджер базы данных
    db_manager = DatabaseManager(DATABASE_URL)
    return db_manager


if __name__ == "__main__":
    db_manager = get_db_manager()
    db_manager.create_tables()
