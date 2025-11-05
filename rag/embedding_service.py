import os
from typing import List, Optional
from sentence_transformers import SentenceTransformer, models
import logging


"""
Модуль получения текстовых эмбеддингов
"""

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Модель эмбеддингов"""
    
    def __init__(self):
        self.model_name = os.getenv("EMBEDDING_MODEL", "deepvk/USER2-base")
        self.model = None
        self.embedding_dim = None
        
    def load_model(self) -> bool:
        """Загрузка модели"""
        try:
            logger.info(f"Загружаем модель для эмбеддингов: {self.model_name}")

            # Загружаем обычную Hugging Face модель
            word_embedding_model = models.Transformer(self.model_name)

            # Добавляем mean pooling
            pooling_model = models.Pooling(
                word_embedding_model.get_word_embedding_dimension(),
                pooling_mode_mean_tokens=True,
                pooling_mode_cls_token=False,
                pooling_mode_max_tokens=False
            )

            # Собираем SentenceTransformer
            self.model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
            # Если уже совместима, то self.model = SentenceTransformer(self.model_name)
            
            test_embedding = self.model.encode(["test"])
            self.embedding_dim = len(test_embedding[0])

            logger.info(f"Модель загружена. Размер эмбеддингов: {self.embedding_dim}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            return False
    
    def encode_text(self, text: str) -> Optional[List[float]]:
        """Получение эмбеддингов для текста"""
        if not self.model:
            logger.error("Модель не загружена")
            return None
        
        try:
            cleaned_text = text.strip()
            if not cleaned_text:
                logger.warning("Пустой текст")
                return None
            
            embedding = self.model.encode([cleaned_text])
            return embedding[0].tolist()
            
        except Exception as e:
            logger.error(f"Ошибка получения эмбеддингов: {e}")
            return None
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[Optional[List[float]]]:
        """Получение эмбеддингов для батчей текста"""
        if not self.model:
            logger.error("Модель не загружена")
            return [None] * len(texts)
        
        try:
            cleaned_texts = [text.strip() for text in texts if text.strip()]
            
            if not cleaned_texts:
                logger.warning("Нет текстов для кодирования")
                return [None] * len(texts)
            
            all_embeddings = []
            
            for i in range(0, len(cleaned_texts), batch_size):
                batch_texts = cleaned_texts[i:i + batch_size]
                logger.info(f"Обрабатываем батч {i//batch_size + 1}/{(len(cleaned_texts) + batch_size - 1)//batch_size}")
                
                batch_embeddings = self.model.encode(batch_texts)
                all_embeddings.extend(batch_embeddings.tolist())
            
            result = []
            text_idx = 0
            
            for original_text in texts:
                if original_text.strip():
                    result.append(all_embeddings[text_idx])
                    text_idx += 1
                else:
                    result.append(None)
            
            logger.info(f"Обработано {len(cleaned_texts)} текстов")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка в получении эмбеддингов для батча: {e}")
            return [None] * len(texts)
    
    def get_embedding_dimension(self) -> Optional[int]:
        """Получить размер эмбеддингов"""
        return self.embedding_dim
    
    def get_model_info(self) -> dict:
        """Получить информацию о модели"""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "is_loaded": self.model is not None
        }


if __name__ == "__main__":
    emb = EmbeddingService()
    emb.load_model()