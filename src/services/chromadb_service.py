"""
ChromaDB 관리 서비스
"""
from typing import List, Dict, Optional, Tuple
import chromadb
import logging
from src.config import CHROMA_PERSIST_DIR, SIMILARITY_THRESHOLD
from src.models.qa_item import QAItem
from src.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class ChromaDBService:
    """ChromaDB 벡터 저장소 관리 서비스"""
    
    def __init__(self, persist_dir: str = CHROMA_PERSIST_DIR, collection_name: str = "qa_items"):
        """ChromaDB 서비스 초기화
        
        Args:
            persist_dir: ChromaDB 저장 디렉토리
            collection_name: 컬렉션 이름 (기본: "qa_items")
        """
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.embedding_service = EmbeddingService()
        
        # ChromaDB 클라이언트 초기화 (최신 방식)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = None
        
        self._initialize_collection()
    
    def _initialize_collection(self) -> None:
        """컬렉션 초기화 (존재하지 않으면 생성)"""
        try:
            # 기존 컬렉션 가져오기 또는 생성
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Collection '{self.collection_name}' initialized")
            
        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            raise
    
    def add_qa_items(self, items: List[QAItem]) -> None:
        """ChromaDB에 Q&A 항목 추가
        
        Args:
            items: 추가할 QAItem 리스트
            
        Raises:
            RuntimeError: 임베딩 생성 또는 저장 실패 시
        """
        if not items:
            logger.warning("No items to add")
            return
        
        try:
            # 임베딩 생성
            texts = [item.question for item in items]
            embeddings = self.embedding_service.embed_texts(texts)
            
            # MetaDB에 추가
            ids = [item.get_hash_key() for item in items]
            # ChromaDB는 비어있지 않은 메타데이터 필요
            metadatas = []
            for item in items:
                metadata = item.metadata or {}
                # 빈 메타데이터에 기본값 추가
                if not metadata:
                    metadata = {"source": "system"}
                metadatas.append(metadata)
            
            documents = [item.answer for item in items]
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            
            logger.info(f"Added {len(items)} items to ChromaDB")
            
        except Exception as e:
            logger.error(f"Error adding QA items: {e}")
            raise RuntimeError(f"Failed to add items to ChromaDB: {e}") from e
    
    def search_similar(self, query: str, top_k: int = 1) -> List[Dict]:
        """유사도 기반으로 Q&A 검색 (Spec FR-009, FR-004)
        
        Args:
            query: 검색 쿼리 (사용자 질문)
            top_k: 반환할 최대 항목 수 (기본: 1, Spec에서 사용자는 1개만 반환)
            
        Returns:
            유사도 임계값(0.7) 이상의 결과 딕셔너리 리스트
            [{"question": str, "answer": str, "similarity": float}, ...]
            
        Raises:
            ValueError: 쿼리가 비어있을 경우
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        try:
            # 쿼리 임베딩 생성
            query_embedding = self.embedding_service.embed_text(query)
            
            # ChromaDB 검색
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # 결과 변환 및 임계값 필터링 (FR-004 참고: 유사도 0.7 이상)
            output = []
            if results["distances"] and len(results["distances"]) > 0:
                for i, distance in enumerate(results["distances"][0]):
                    # ChromaDB는 거리 반환 (0~1, 0에 가까울수록 유사)
                    # 유사도 = 1 - 거리
                    similarity = 1 - distance
                    
                    if similarity >= SIMILARITY_THRESHOLD:
                        output.append({
                            "question": results["ids"][0][i],  # 역정규화된 질문 키
                            "answer": results["documents"][0][i] if results["documents"] else "",
                            "similarity": round(similarity, 4),
                            "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                        })
            
            logger.info(f"Search query '{query}' returned {len(output)} results")
            return output
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise RuntimeError(f"Failed to search: {e}") from e
    
    def update_qa_item(self, item: QAItem) -> None:
        """기존 Q&A 항목 업데이트 (Spec FR-008: 중복 질문 덮어쓰기)
        
        Args:
            item: 업데이트할 QAItem
            
        Raises:
            RuntimeError: 업데이트 실패 시
        """
        try:
            # 기존 항목이 있으면 삭제
            item_id = item.get_hash_key()
            try:
                self.collection.delete(ids=[item_id])
                logger.debug(f"Deleted existing item with id: {item_id}")
            except Exception:
                # 항목이 없을 수 있음, 무시
                pass
            
            # 새 항목 추가
            self.add_qa_items([item])
            logger.info(f"Updated QA item: {item.question}")
            
        except Exception as e:
            logger.error(f"Error updating QA item: {e}")
            raise RuntimeError(f"Failed to update item: {e}") from e
    
    def delete_qa_item(self, question: str) -> bool:
        """질문 기반으로 항목 삭제
        
        Args:
            question: 삭제할 질문
            
        Returns:
            삭제 성공 여부
        """
        try:
            item_id = question.strip().lower()
            self.collection.delete(ids=[item_id])
            logger.info(f"Deleted QA item with question: {question}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting QA item: {e}")
            raise RuntimeError(f"Failed to delete item: {e}") from e
    
    def count_items(self) -> int:
        """컬렉션의 총 항목 수
        
        Returns:
            항목 수
        """
        try:
            count = self.collection.count()
            logger.debug(f"Collection has {count} items")
            return count
            
        except Exception as e:
            logger.error(f"Error counting items: {e}")
            raise
    
    def clear_collection(self) -> None:
        """컬렉션의 모든 항목 제거
        
        Raises:
            RuntimeError: 제거 실패 시
        """
        try:
            # 컬렉션 삭제 후 재생성
            self.client.delete_collection(name=self.collection_name)
            self._initialize_collection()
            logger.info(f"Cleared collection '{self.collection_name}'")
            
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise RuntimeError(f"Failed to clear collection: {e}") from e
    
    def persist(self) -> None:
        """데이터 저장 (필요시 명시적 호출)"""
        try:
            self.client.persist()
            logger.info("ChromaDB data persisted")
            
        except Exception as e:
            logger.warning(f"Error persisting data: {e}")
