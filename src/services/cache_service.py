"""Cache service for embedding optimization."""

from typing import Optional, List
import time

from src.utils.cache import LRUCache, get_cache


class CacheService:
    """
    캐시 서비스 (LRU 캐시 래퍼)
    
    EmbeddingService와 협력하여 임베딩 결과를 캐싱
    """
    
    def __init__(self, cache: Optional[LRUCache] = None):
        """
        캐시 서비스 초기화
        
        Args:
            cache: LRUCache 인스턴스 (기본: 싱글톤)
        """
        self.cache = cache or get_cache()
    
    def get_embedding(self, question: str) -> Optional[List[float]]:
        """
        캐시에서 임베딩 조회
        
        Args:
            question: 질문 텍스트
        
        Returns:
            임베딩 벡터 또는 None (캐시 미스)
        """
        key = self._hash_question(question)
        start_time = time.time()
        
        embedding = self.cache.get(key)
        
        elapsed_ms = (time.time() - start_time) * 1000
        self._update_response_time(elapsed_ms)
        
        return embedding
    
    def set_embedding(self, question: str, embedding: List[float]) -> None:
        """
        캐시에 임베딩 저장
        
        Args:
            question: 질문 텍스트
            embedding: 임베딩 벡터
        """
        key = self._hash_question(question)
        self.cache.set(key, embedding)
    
    def clear(self) -> None:
        """전체 캐시 초기화"""
        self.cache.clear()
        self.cache.reset_stats()
    
    def get_stats(self) -> dict:
        """
        캐시 통계 조회
        
        Returns:
            통계 딕셔너리
        """
        stats = self.cache.get_stats()
        return stats.to_dict()
    
    @staticmethod
    def _hash_question(question: str) -> str:
        """질문 텍스트를 해시로 변환"""
        return LRUCache.hash_question(question)
    
    def _update_response_time(self, elapsed_ms: float) -> None:
        """
        평균 응답 시간 업데이트
        
        Args:
            elapsed_ms: 응답 시간 (ms)
        """
        stats = self.cache.stats
        
        # 이동 평균: (기존*n + 새값) / (n+1)
        total = stats.total_requests
        old_avg = stats.avg_response_time_ms
        
        if total > 0:
            stats.avg_response_time_ms = (old_avg * (total - 1) + elapsed_ms) / total
        else:
            stats.avg_response_time_ms = elapsed_ms


# 싱글톤 인스턴스
_default_service: Optional[CacheService] = None

def get_cache_service() -> CacheService:
    """
    기본 캐시 서비스 반환 (싱글톤)
    
    Returns:
        CacheService 인스턴스
    """
    global _default_service
    if _default_service is None:
        _default_service = CacheService()
    return _default_service

def reset_cache_service() -> None:
    """캐시 서비스 초기화 (테스트 목적)"""
    global _default_service
    _default_service = None
