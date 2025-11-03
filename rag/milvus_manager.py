from typing import List, Dict, Any, Optional
from pymilvus import (
    connections, Collection, CollectionSchema, FieldSchema, DataType,
    utility, MilvusException
)
import logging

logger = logging.getLogger(__name__)


class MilvusManager:
    """Сервис для работы с Milvus"""
    
    def __init__(self, host: str = "localhost", port: int = 19530):
        self.host = host
        self.port = port
        self.connection_alias = "default"
        self.collection_name = "law_paragraphs"
        
    def connect(self) -> bool:
        """Подключение к Milvus серверу"""
        try:
            connections.connect(
                alias=self.connection_alias,
                host=self.host,
                port=self.port
            )
            logger.info(f"Установлено подключение к Milvus: {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Ошибка соединения: {e}")
            return False
    
    def disconnect(self):
        """Отключение от Milvus сервера"""
        try:
            connections.disconnect(alias=self.connection_alias)
            logger.info("Отключение от Milvus")
        except Exception as e:
            logger.error(f"Ошибка отключения: {e}")
    
    def create_collection(self, embedding_dim: int = 384) -> bool:
        """Создание и первичное заполнение коллекции"""
        try:
            if utility.has_collection(self.collection_name):
                logger.info(f"Коллекция {self.collection_name} уже существует")
                return True
            
            fields = [
                FieldSchema(
                    name="id", 
                    dtype=DataType.INT64, 
                    is_primary=True, 
                    auto_id=True
                ),
                FieldSchema(
                    name="paragraph_id", 
                    dtype=DataType.INT64
                ),
                FieldSchema(
                    name="embedding", 
                    dtype=DataType.FLOAT_VECTOR, 
                    dim=embedding_dim
                )
            ]
            
            schema = CollectionSchema(
                fields=fields,
                description="Коллекция эмбеддингов пунктов закона"
            )
            
            collection = Collection(
                name=self.collection_name,
                schema=schema,
                using=self.connection_alias
            )
            
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            
            collection.create_index(
                field_name="embedding",
                index_params=index_params
            )
            
            logger.info(f"Коллекция {self.collection_name} создана")
            return True
            
        except MilvusException as e:
            logger.error(f"Ошибка создания коллекции: {e}")
            return False

    def delete_collection(self) -> bool:
        try:
            if utility.has_collection(self.collection_name):
                collection = Collection(
                    name=self.collection_name,
                    using=self.connection_alias
                )

                collection.drop()
                logger.info("✅ Коллекция полностью удалена")
                return True
            else:
                logger.info("✅ Коллекции не было, нечего удалять")
                return True

        except Exception as e:
            logger.error(f"Ошибка удаления коллекции: {e}")
            return False

    def get_collection(self) -> Optional[Collection]:
        """Получение коллекции"""
        try:
            if not utility.has_collection(self.collection_name):
                logger.error(f"Коллекция {self.collection_name} не существует")
                return None
            
            collection = Collection(
                name=self.collection_name,
                using=self.connection_alias
            )
            return collection
            
        except MilvusException as e:
            logger.error(f"Ошибка получения коллекции: {e}")
            return None
    
    def insert_data(self, data: List[Dict[str, Any]]) -> bool:
        """Добавление данных в коллекцию"""
        try:
            collection = self.get_collection()
            if not collection:
                return False

            insert_data = [
                [item["paragraph_id"] for item in data],
                [item["embedding"] for item in data]
            ]
            
            collection.insert(insert_data)
            collection.flush()
            
            logger.info(f"✔️ Добавлено {len(data)} записей")
            return True
            
        except MilvusException as e:
            logger.error(f"Ошибка добавления: {e}")
            return False
    
    def search_similar(
        self, 
        query_embedding: List[float], 
        top_k: int = 3,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Поиск похожих пунктов закона"""
        try:
            collection = self.get_collection()
            if not collection:
                return []
            
            collection.load()
            
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["paragraph_id"]
            )
            
            similar_paragraphs = []
            for hits in results:
                for hit in hits:
                    if hit.score >= score_threshold:
                        similar_paragraphs.append({
                            "paragraph_id": hit.entity.get("paragraph_id"),
                            "similarity_score": float(hit.score)
                        })
            
            logger.info(f"Найдено {len(similar_paragraphs)} похожих пунктов")
            return similar_paragraphs
            
        except MilvusException as e:
            logger.error(f"Ошибка поиска: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Получение статистики коллекции"""
        try:
            collection = self.get_collection()
            if not collection:
                return {}
            
            stats = {
                "name": self.collection_name,
                "num_entities": collection.num_entities,
                "description": collection.description
            }
            
            return stats
            
        except MilvusException as e:
            logger.error(f"Stats error: {e}")
            return {}


milvus_manager = MilvusManager()