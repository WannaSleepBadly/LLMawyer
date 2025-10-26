"""
Конфигурация для подключения к PostgreSQL базе данных.
"""
import os

class DatabaseConfig:
    """Конфигурация базы данных"""
    
    # Параметры подключения к PostgreSQL
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'llmawyer')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    
    @classmethod
    def get_database_url(cls) -> str:
        """Получение URL подключения к базе данных"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    

def setup_database():
    """Настройка базы данных"""
    from .models import DatabaseManager
    
    db_url = DatabaseConfig.get_database_url()
    db_manager = DatabaseManager(db_url)
    
    # Тестируем подключение
    if not db_manager.test_connection():
        raise ConnectionError("Не удалось подключиться к базе данных")
    
    # Создаем таблицы
    db_manager.create_tables()
    
    print("✅ База данных настроена успешно")
    return db_manager


if __name__ == "__main__":
    # Настройка базы данных при запуске скрипта
    try:
        db_manager = setup_database()
    except Exception as e:
        print(f"❌ Ошибка настройки: {e}")
        exit(1)
