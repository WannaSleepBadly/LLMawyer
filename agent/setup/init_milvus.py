import logging
import os
import sys

from dotenv import load_dotenv
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

from LLMawyer.agent.agent_dependencies import get_retriever
from LLMawyer.agent.embedding_service import EmbeddingService
from LLMawyer.law_data.config import get_db_manager
from LLMawyer.law_data.models import Law, LawChapter, LawParagraph, LawPart

"""
Скрипт для инициализации и заполнения Milvus базы данных эмбеддингами пунктов закона.
"""

logging.basicConfig(
    level=logging.DEBUG,  # Уровень DEBUG покажет ВСЕ сообщения
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],  # Вывод в консоль
)

logger = logging.getLogger(__name__)


def main():
    """Основная функция для инициализации RAG системы"""

    # Загружаем переменные окружения
    load_dotenv()
    batch_size = 32

    # Проверяем наличие EMBEDDING_MODEL в .env
    embedding_model = os.getenv("EMBEDDING_MODEL")
    if not embedding_model:
        logger.error("Переменная EMBEDDING_MODEL не найдена в .env файле")
        return False

    logger.info(f"Используем модель эмбеддингов: {embedding_model}")

    try:

        collection_name = os.getenv("MILVUS_COLLECTION_NAME")
        alias = os.getenv("MILVUS_DB_NAME")
        uri = os.getenv("MILVUS_URI").split("tcp://")[1].split(":")
        host, port = uri[0], uri[1]
        connections.connect(alias=alias, host=host, port=port)

        fields = [
            FieldSchema(name="paragraph_id", dtype=DataType.INT64, is_primary=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
        ]

        schema = CollectionSchema(fields, description="Law paragraphs with text")
        collection = Collection(name=collection_name, using=alias, schema=schema)

        if utility.has_collection("law_paragraphs"):
            response = input("Хотите перезаполнить коллекцию? (y/n): ")
            if response.lower() == "y":
                collection.drop()

        # Получаем тексты из postgres
        db_manager = get_db_manager()
        db_session = db_manager.get_session()

        paragraphs_query = (
            db_session.query(LawParagraph)
            .join(LawPart, LawParagraph.part_id == LawPart.part_id)
            .join(LawChapter, LawPart.chapter_id == LawChapter.chapter_id)
            .join(Law, LawChapter.law_id == Law.law_id)
            .all()
        )
        db_session.close()

        logger.info(f"Найдено {len(paragraphs_query)} пунктов для обработки")

        # Получаем эмбеддинги
        embedder = EmbeddingService()

        for i in range(0, len(paragraphs_query), batch_size):
            batch = paragraphs_query[i : i + batch_size]
            logger.info(
                f"Обрабатываем батч {i // batch_size + 1}/{(len(paragraphs_query) + batch_size - 1) // batch_size}"
            )

            batch_data = []
            texts = []

            for paragraph in batch:
                batch_data.append(
                    {"paragraph_id": paragraph.paragraph_id, "text": paragraph.content}
                )
                texts.append(paragraph.content)

            embeddings = embedder.embed_documents(texts, batch_size)

            for j, embedding in enumerate(embeddings):
                if embedding is not None:
                    batch_data[j]["vector"] = embedding

            insert_data = [
                [item["paragraph_id"] for item in batch_data],
                [item["vector"] for item in batch_data],
                [item["text"] for item in batch_data],
            ]

            collection.insert(insert_data)
            collection.flush()
            logger.info(f"Добавлено {len(insert_data)} записей.")

        logger.info(f"В коллекции {collection.num_entities} сущностей.")

        # Тестирование
        test_rag()

        return True

    except Exception as e:
        logger.error(f"❌ Ошибка инициализации: {e}")
        return False


def test_rag():
    # Тестируем поиск
    logger.info("Тестируем поиск...")
    test_query = "реклама не должна содержать недостоверную информацию"
    retriever = get_retriever()
    results = retriever.invoke(test_query)
    if results:
        logger.info(f"Тестовый поиск успешен. Найдено {len(results)} результатов:")
        for i, result in enumerate(results[:3], 1):
            logger.info(f"  {i}. {result.page_content[:100]})")
    else:
        logger.warning("Тестовый поиск не вернул результатов")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
