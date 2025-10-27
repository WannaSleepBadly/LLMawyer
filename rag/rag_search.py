from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from parser.models import LawParagraph, LawPart, LawChapter, Law, SessionLocal
from .milvus_manager import MilvusManager
from .embedding_service import EmbeddingService
import logging

logger = logging.getLogger(__name__)


class RAGSearchService:
    """Service for RAG search of similar law paragraphs"""
    
    def __init__(self, milvus_host: str = "localhost", milvus_port: int = 19530):
        self.milvus_manager = MilvusManager(milvus_host, milvus_port)
        self.embedding_service = EmbeddingService()
        self.db_session = None
        
    def initialize(self) -> bool:
        """Initialize service (connect to Milvus and load model)"""
        try:
            if not self.milvus_manager.connect():
                return False
            
            if not self.embedding_service.load_model():
                return False
            
            embedding_dim = self.embedding_service.get_embedding_dimension()
            if not self.milvus_manager.create_collection(embedding_dim):
                return False
            
            logger.info("RAG service initialized")
            return True
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False
    
    def populate_milvus_from_postgres(self, batch_size: int = 100) -> bool:
        """Populate Milvus with data from PostgreSQL"""
        try:
            db = SessionLocal()
            
            paragraphs_query = db.query(LawParagraph).join(
                LawPart, LawParagraph.part_id == LawPart.part_id
            ).join(
                LawChapter, LawPart.chapter_id == LawChapter.chapter_id
            ).join(
                Law, LawChapter.law_id == Law.law_id
            ).all()
            
            logger.info(f"Found {len(paragraphs_query)} paragraphs to process")
            
            total_processed = 0
            
            for i in range(0, len(paragraphs_query), batch_size):
                batch = paragraphs_query[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(paragraphs_query) + batch_size - 1)//batch_size}")
                
                batch_data = []
                texts = []
                
                for paragraph in batch:
                    batch_data.append({
                        "paragraph_id": paragraph.paragraph_id
                    })
                    texts.append(paragraph.content)
                
                embeddings = self.embedding_service.encode_batch(texts, batch_size)
                
                for j, embedding in enumerate(embeddings):
                    if embedding is not None:
                        batch_data[j]["embedding"] = embedding
                
                valid_data = [item for item in batch_data if "embedding" in item]
                
                if valid_data:
                    if self.milvus_manager.insert_data(valid_data):
                        total_processed += len(valid_data)
                        logger.info(f"Processed {len(valid_data)} records in batch")
                    else:
                        logger.error("Insert error")
                        return False
            
            logger.info(f"Total processed {total_processed} paragraphs")
            db.close()
            return True
            
        except Exception as e:
            logger.error(f"Population error: {e}")
            if self.db_session:
                self.db_session.close()
            return False
    
    def search_similar_paragraphs(
        self, 
        query_text: str, 
        top_k: int = 10,
        score_threshold: float = 0.7,
        law_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search similar paragraphs by text"""
        try:
            query_embedding = self.embedding_service.encode_text(query_text)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            milvus_results = self.milvus_manager.search_similar(
                query_embedding, top_k, score_threshold
            )
            
            similar_paragraphs = []
            for result in milvus_results:
                paragraph_id = result["paragraph_id"]
                similarity_score = result["similarity_score"]
                
                details = self.get_paragraph_details(paragraph_id)
                if details:
                    if law_code and details["law"]["code"] != law_code:
                        continue
                    
                    similar_paragraphs.append({
                        "paragraph_id": paragraph_id,
                        "similarity_score": similarity_score,
                        "content": details["content"],
                        "law_code": details["law"]["code"],
                        "law_name": details["law"]["name"],
                        "chapter_number": details["chapter"]["number"],
                        "chapter_title": details["chapter"]["title"],
                        "part_number": details["part"]["number"],
                        "part_title": details["part"]["title"],
                        "paragraph_number": details["paragraph_number"]
                    })
            
            logger.info(f"Found {len(similar_paragraphs)} similar paragraphs")
            return similar_paragraphs
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_paragraph_details(self, paragraph_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed paragraph information from PostgreSQL"""
        try:
            db = SessionLocal()
            
            paragraph = db.query(LawParagraph).join(
                LawPart, LawParagraph.part_id == LawPart.part_id
            ).join(
                LawChapter, LawPart.chapter_id == LawChapter.chapter_id
            ).join(
                Law, LawChapter.law_id == Law.law_id
            ).filter(LawParagraph.paragraph_id == paragraph_id).first()
            
            if not paragraph:
                logger.warning(f"Paragraph with ID {paragraph_id} not found")
                db.close()
                return None
            
            details = {
                "paragraph_id": paragraph.paragraph_id,
                "content": paragraph.content,
                "paragraph_number": paragraph.number,
                "part": {
                    "part_id": paragraph.part.part_id,
                    "number": paragraph.part.number,
                    "title": paragraph.part.title
                },
                "chapter": {
                    "chapter_id": paragraph.part.chapter.chapter_id,
                    "number": paragraph.part.chapter.number,
                    "title": paragraph.part.chapter.title
                },
                "law": {
                    "law_id": paragraph.part.chapter.law.law_id,
                    "code": paragraph.part.chapter.law.code,
                    "name": paragraph.part.chapter.law.name,
                    "source_url": paragraph.part.chapter.law.source_url
                }
            }
            
            db.close()
            return details
            
        except Exception as e:
            logger.error(f"Get details error: {e}")
            if self.db_session:
                self.db_session.close()
            return None
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get Milvus collection statistics"""
        return self.milvus_manager.get_collection_stats()
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.milvus_manager.disconnect()
            if self.db_session:
                self.db_session.close()
            logger.info("Resources cleaned")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

