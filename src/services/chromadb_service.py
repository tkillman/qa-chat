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
    
    # 싱글톤 인스턴스 캐시
    _instances = {}
    
    def __new__(cls, persist_dir: str = CHROMA_PERSIST_DIR, collection_name: str = "qa_items"):
        """싱글톤 패턴: 동일한 persist_dir + collection_name 조합은 같은 인스턴스 반환"""
        key = (persist_dir, collection_name)
        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance
            instance._initialized = False
        return cls._instances[key]
    
    def __init__(self, persist_dir: str = CHROMA_PERSIST_DIR, collection_name: str = "qa_items"):
        """ChromaDB 서비스 초기화 (최초 1회만 수행)
        
        Args:
            persist_dir: ChromaDB 저장 디렉토리
            collection_name: 컬렉션 이름 (기본: "qa_items")
        """
        # 이미 초기화된 경우 스킵
        if self._initialized:
            return
        
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.embedding_service = EmbeddingService()
        
        # ChromaDB 클라이언트 초기화 (최신 방식)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = None
        
        self._initialize_collection()
        self._initialized = True
    
    def _initialize_collection(self) -> None:
        """컬렉션 초기화 (존재하면 재사용, 손상되면 재생성)"""
        try:
            # 기존 컬렉션 목록 확인
            try:
                existing_collections = self.client.list_collections()
                for col in existing_collections:
                    if col.name == self.collection_name:
                        # 기존 컬렉션 재사용 시도
                        try:
                            self.collection = self.client.get_collection(name=self.collection_name)
                            # 간단한 액세스 테스트 (손상 확인)
                            self.collection.count()
                            logger.info(f"Reusing existing collection '{self.collection_name}'")
                            return
                        except Exception as col_error:
                            logger.warning(f"Existing collection is corrupted, will recreate: {col_error}")
                            # 손상된 컬렉션 삭제 후 재생성
                            try:
                                self.client.delete_collection(name=self.collection_name)
                            except:
                                pass
                            break
            except Exception as e:
                logger.debug(f"Error checking existing collections: {e}")
            
            # 새로운 컬렉션 생성
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection '{self.collection_name}'")
            
        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            raise
    
    def _ensure_collection_healthy(self) -> None:
        """컬렉션 상태 확인 및 손상 시 재생성"""
        try:
            if self.collection is None:
                self._initialize_collection()
                return
            
            # 컬렉션 접근 가능성 테스트
            try:
                self.collection.count()
            except Exception as e:
                logger.warning(f"Collection is unhealthy, rebuilding: {e}")
                try:
                    self.client.delete_collection(name=self.collection_name)
                except:
                    pass
                self._initialize_collection()
        except Exception as e:
            logger.error(f"Error ensuring collection health: {e}")
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
            # 메타데이터 준비 (답변 포함)
            ids = [item.get_hash_key() for item in items]
            metadatas = []
            documents = [item.question for item in items]  # 임베딩할 텍스트는 질문
            
            for item in items:
                # 메타데이터에 답변 저장
                metadata = item.metadata or {}
                if not metadata:
                    metadata = {}
                metadata["answer"] = item.answer  # 답변을 메타데이터에 추가
                metadatas.append(metadata)
            
            # ChromaDB 기본 임베딩 함수 사용
            # documents의 질문 텍스트가 임베딩되고 유사 검색에 사용됨
            self.collection.add(
                ids=ids,
                documents=documents,  # 질문이 임베딩될 텍스트
                metadatas=metadatas   # 메타데이터에 답변 저장
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
            # ChromaDB 기본 임베딩 함수를 사용하여 검색
            # query_texts를 사용하면 ChromaDB가 자동으로 임베딩 생성
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                include=["documents", "metadatas", "distances", "ids"]
            )
            
            # 결과 변환 및 임계값 필터링 (FR-004 참고: 유사도 0.7 이상)
            output = []
            if results["distances"] and len(results["distances"]) > 0:
                for i, distance in enumerate(results["distances"][0]):
                    # ChromaDB는 거리 반환 (0~1, 0에 가까울수록 유사)
                    # 유사도 = 1 - 거리
                    similarity = 1 - distance
                    
                    if similarity >= SIMILARITY_THRESHOLD:
                        metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                        output.append({
                            "question": results["documents"][0][i],  # 질문 텍스트
                            "answer": metadata.get("answer", ""),  # 메타데이터에서 답변 추출
                            "similarity": round(similarity, 4),
                            "metadata": metadata
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
    
    def delete(self, qa_id: str) -> None:
        """ID로 항목 삭제
        
        Args:
            qa_id: 삭제할 Q&A 항목의 Hash ID
            
        Raises:
            KeyError: 항목을 찾을 수 없는 경우
            RuntimeError: 삭제 작업 실패
        """
        try:
            if not qa_id:
                raise ValueError("qa_id는 빈 값이 될 수 없습니다")
            
            # 항목 존재 여부 확인
            result = self.collection.get(ids=[qa_id])
            if not result or not result.get("ids"):
                raise KeyError(f"항목을 찾을 수 없습니다: {qa_id}")
            
            # 항목 삭제
            self.collection.delete(ids=[qa_id])
            logger.info(f"Deleted QA item: {qa_id}")
            
        except KeyError:
            raise
        except Exception as e:
            logger.error(f"Error deleting QA item {qa_id}: {e}")
            raise RuntimeError(f"Failed to delete item: {e}") from e
    
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


# 글로벌 인스턴스
_chromadb_service = None


def get_chromadb_service() -> ChromaDBService:
    """ChromaDB 서비스 인스턴스 반환 (싱글톤)
    
    Returns:
        ChromaDBService 인스턴스
    """
    global _chromadb_service
    if _chromadb_service is None:
        _chromadb_service = ChromaDBService()
    return _chromadb_service
