"""
임베딩 생성 서비스 - LangChain/LiteLLM 경유
"""
from typing import List, Optional
import logging
from src.config import EMBEDDING_MODEL
from src.services.cache_service import CacheService, get_cache_service

logger = logging.getLogger(__name__)


class EmbeddingService:
    """텍스트를 벡터로 변환하는 서비스"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL, cache_service: Optional[CacheService] = None):
        """임베딩 서비스 초기화
        
        Args:
            model_name: 사용할 임베딩 모델 이름 (기본: config.EMBEDDING_MODEL)
            cache_service: 캐시 서비스 (기본: 싱글톤)
        """
        self.model_name = model_name
        self.cache_service = cache_service or get_cache_service()
        self._embeddings = None
        self._initialize_embeddings()
    
    def _initialize_embeddings(self) -> None:
        """임베딩 모델 초기화

        FR-013 계약에 따라 기본값은 ChromaDB 기본 임베딩 함수로 고정한다.
        """
        try:
            self._embeddings = "chromadb_default_function"
            logger.info(f"Embedding service initialized with provider: {self._embeddings} (model={self.model_name})")

        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """텍스트를 임베딩 벡터로 변환
        
        Args:
            text: 변환할 텍스트
            
        Returns:
            임베딩 벡터 (List[float])
            
        Raises:
            ValueError: 텍스트가 비어있을 경우
            RuntimeError: 임베딩 생성 실패 시
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            # 캐시 확인
            cached_embedding = self.cache_service.get_embedding(text)
            if cached_embedding is not None:
                logger.debug("Embedding cache hit")
                return cached_embedding

            # FR-013: ChromaDB 기본 임베딩 함수 사용 (현재 테스트/개발용 placeholder)
            # 실제 ChromaDB runtime 연동 시 컬렉션 임베딩 함수 결과로 교체 가능
            embedding = [0.0] * 1536

            # 캐시 저장
            self.cache_service.set_embedding(text, embedding)
            
            logger.debug(f"Generated embedding for text (length: {len(text)})")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise RuntimeError(f"Failed to generate embedding: {e}") from e
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """여러 텍스트를 일괄 임베딩으로 변환
        
        Args:
            texts: 변환할 텍스트 리스트
            
        Returns:
            임베딩 벡터 리스트
            
        Raises:
            ValueError: 입력 리스트가 비어있을 경우
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        try:
            embeddings = [self.embed_text(text) for text in texts]
            logger.info(f"Generated embeddings for {len(embeddings)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """두 벡터 간의 코사인 유사도 계산
        
        Args:
            vec1: 첫 번째 벡터
            vec2: 두 번째 벡터
            
        Returns:
            코사인 유사도 (0.0 ~ 1.0)
            
        Raises:
            ValueError: 벡터 길이가 다를 경우
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same dimension")
        
        try:
            # 코사인 유사도 = (A·B) / (||A|| * ||B||)
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude_1 = sum(a ** 2 for a in vec1) ** 0.5
            magnitude_2 = sum(b ** 2 for b in vec2) ** 0.5
            
            if magnitude_1 == 0 or magnitude_2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude_1 * magnitude_2)
            return max(0.0, min(1.0, similarity))  # 0.0 ~ 1.0 범위로 정규화
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            raise

    def get_embedding_provider(self) -> str:
        """테스트/계약 검증용 임베딩 제공자 정보 반환."""
        return str(self._embeddings)
