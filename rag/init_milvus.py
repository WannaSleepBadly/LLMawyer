import os
import sys
import logging
from dotenv import load_dotenv
from .rag_search import RAGSearchService

"""
Скрипт для инициализации и заполнения Milvus базы данных эмбеддингами пунктов закона.
"""

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Основная функция для инициализации RAG системы"""
    
    # Загружаем переменные окружения
    load_dotenv()
    
    # Проверяем наличие EMBEDDING_MODEL в .env
    embedding_model = os.getenv("EMBEDDING_MODEL")
    if not embedding_model:
        logger.error("❌ Переменная EMBEDDING_MODEL не найдена в .env файле")
        logger.info("Добавьте в .env файл: EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        return False
    
    logger.info(f"🔄 Используем модель эмбеддингов: {embedding_model}")
    
    # Инициализируем RAG сервис
    rag_service = RAGSearchService()
    
    try:
        # Инициализируем сервис
        logger.info("🔄 Инициализируем RAG сервис...")
        if not rag_service.initialize():
            logger.error("❌ Не удалось инициализировать RAG сервис")
            return False
        
        # Получаем статистику коллекции
        stats = rag_service.get_collection_stats()
        logger.info(f"📊 Статистика коллекции: {stats}")
        
        # Проверяем, есть ли уже данные в коллекции
        if stats.get("num_entities", 0) > 0:
            logger.info(f"⚠️ В коллекции уже есть {stats['num_entities']} записей")
            response = input("Хотите перезаполнить коллекцию? (y/n): ")
            if response.lower() == 'y':
                logger.info("🔄 Перезаполняем коллекцию...")
                if not rag_service.populate_milvus_from_postgres(drop_existing=True):
                    logger.error("❌ Не удалось заполнить коллекцию")
                    return False
            else:
                logger.info("✅ Используем существующие данные")
        else:
            # Заполняем коллекцию данными из PostgreSQL
            logger.info("🔄 Заполняем коллекцию данными из PostgreSQL...")
            if not rag_service.populate_milvus_from_postgres(drop_existing=False):
                logger.error("❌ Не удалось заполнить коллекцию")
                return False
        
        # Получаем финальную статистику
        final_stats = rag_service.get_collection_stats()
        logger.info(f"📊 Финальная статистика коллекции: {final_stats}")
        
        # Тестируем поиск
        logger.info("🔄 Тестируем поиск...")
        test_query = "реклама не должна содержать недостоверную информацию"
        results = rag_service.search_similar_paragraphs(test_query, top_k=5)
        
        if results:
            logger.info(f"✅ Тестовый поиск успешен. Найдено {len(results)} результатов:")
            for i, result in enumerate(results[:3], 1):
                logger.info(f"  {i}. {result['content'][:100]}... (score: {result['similarity_score']:.3f})")
                logger.info(result)
        else:
            logger.warning("⚠️ Тестовый поиск не вернул результатов")
        
        logger.info("✅ RAG система успешно инициализирована!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации: {e}")
        return False
    
    finally:
        # Очищаем ресурсы
        rag_service.cleanup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
