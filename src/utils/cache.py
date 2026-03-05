"""LRU (Least Recently Used) Cache implementation for embeddings."""

from collections import OrderedDict
from typing import Optional, List
import hashlib
import sys
import threading

from src.models.cache_models import CacheEntry, CacheStats


class LRUCache:
    """
    스레드 안전한 LRU (Least Recently Used) 캐시 구현
    
    임베딩 결과를 메모리에 LRU 정책으로 저장하여 성능 최적화
    - 캐시 히트: <1ms
    - 캐시 미스: <2ms (제거 포함)
    - 최대 메모리: 5000개 항목 = ~30MB
    """
    
    def __init__(self, max_size: int = 5000):
        """
        LRU 캐시 초기화
        
        Args:
            max_size: 최대 캐시 크기 (기본: 5000)
        """
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.max_size = max_size
        self.stats = CacheStats(max_cache_size=max_size)
        self._lock = threading.RLock()  # 스레드 안전성
    
    def get(self, key: str) -> Optional[List[float]]:
        """
        캐시에서 임베딩 조회
        
        히트 시 해당 항목을 최신 위치로 이동 (LRU)
        
        Args:
            key: 질문 텍스트의 SHA256 해시
        
        Returns:
            임베딩 벡터 (List[float]) 또는 None (캐시 미스)
        
        Raises:
            ValueError: 잘못된 키 형식
        """
        if not isinstance(key, str) or len(key) != 64:
            raise ValueError(f"Key must be SHA256 hash (64 chars), got {len(key) if isinstance(key, str) else 'not string'}")
        
        with self._lock:
            if key in self.cache:
                # 캐시 히트: 항목을 최신 위치로 이동
                entry: CacheEntry = self.cache[key]
                entry.record_access()
                self.cache.move_to_end(key)
                
                # 통계 업데이트
                self.stats.cache_hits += 1
                self.stats.total_requests += 1
                
                return entry.embedding
            
            # 캐시 미스
            self.stats.cache_misses += 1
            self.stats.total_requests += 1
            return None
    
    def set(self, key: str, embedding: List[float]) -> None:
        """
        캐시에 임베딩 저장
        
        캐시가 가득 차면 LRU 정책에 따라 가장 오래된 항목 제거
        
        Args:
            key: 질문 텍스트의 SHA256 해시
            embedding: 임베딩 벡터 (List[float], 1536개)
        
        Raises:
            ValueError: 임베딩 크기 불일치 (1536 필수)
            ValueError: 키 형식 오류
        """
        if not isinstance(embedding, list) or len(embedding) != 1536:
            raise ValueError(f"Embedding must be list of 1536 floats, got {len(embedding) if isinstance(embedding, list) else 'not list'}")
        if not isinstance(key, str) or len(key) != 64:
            raise ValueError(f"Key must be SHA256 hash (64 chars), got {len(key) if isinstance(key, str) else 'not string'}")
        
        with self._lock:
            # 기존 키 업데이트 시 최신 위치로 이동
            if key in self.cache:
                self.cache.move_to_end(key)
            
            # 새 항목 생성 및 저장
            entry = CacheEntry(
                key=key,
                embedding=embedding,
                created_at=self._get_utc_now()
            )
            self.cache[key] = entry
            
            # 캐시 크기 초과 시 LRU 제거
            if len(self.cache) > self.max_size:
                # FIFO order (가장 오래된 항목이 처음)
                oldest_key, oldest_entry = self.cache.popitem(last=False)
            
            # 통계 업데이트
            self.stats.cache_size = len(self.cache)
            self.stats.memory_used_mb = self._estimate_memory_usage()
    
    def clear(self) -> None:
        """
        전체 캐시 초기화
        
        관리자가 새 Q&A 배치를 업로드할 때, 또는 임베딩 모델 변경 시 호출
        """
        with self._lock:
            self.cache.clear()
            self.stats.cache_size = 0
            self.stats.memory_used_mb = 0.0
    
    def get_stats(self) -> CacheStats:
        """
        캐시 통계 조회
        
        Returns:
            CacheStats 객체
        """
        with self._lock:
            stats_copy = CacheStats(
                total_requests=self.stats.total_requests,
                cache_hits=self.stats.cache_hits,
                cache_misses=self.stats.cache_misses,
                avg_response_time_ms=self.stats.avg_response_time_ms,
                cache_size=self.stats.cache_size,
                max_cache_size=self.stats.max_cache_size,
                memory_used_mb=self.stats.memory_used_mb,
            )
            return stats_copy
    
    def reset_stats(self) -> None:
        """통계 초기화 (테스트 목적)"""
        with self._lock:
            self.stats = CacheStats(max_cache_size=self.max_size)
            self.stats.cache_size = len(self.cache)
            self.stats.memory_used_mb = self._estimate_memory_usage()
    
    @staticmethod
    def hash_question(question: str) -> str:
        """
        질문 텍스트를 SHA256 해시로 변환
        
        Args:
            question: 질문 텍스트
        
        Returns:
            SHA256 해시 (64자 16진수)
        
        Examples:
            >>> key = LRUCache.hash_question("테스트 질문")
            >>> print(len(key))
            64
        """
        normalized = " ".join(question.strip().lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    @staticmethod
    def _get_utc_now():
        """UTC 현재시간 반환 (테스트 용이성을 위해 별도 메서드)"""
        from datetime import datetime, UTC
        return datetime.now(UTC)
    
    def _estimate_memory_usage(self) -> float:
        """
        캐시 메모리 사용량 추정 (MB)
        
        계산:
        - 16 바이트 (Python 객체 헤더)
        - 8 바이트 (key 참조)
        - 8 바이트 (embedding 참조)
        - 4KB (메타데이터)
        - 1536 * 4바이트 (embedding = 6144바이트)
        
        항목당: ~6.2KB
        5000개: ~31MB
        """
        bytes_per_entry = 6200  # 약 6KB per entry
        total_bytes = len(self.cache) * bytes_per_entry
        return total_bytes / (1024 * 1024)  # Convert to MB
    
    def __len__(self) -> int:
        """캐시 항목 수"""
        return len(self.cache)
    
    def __repr__(self) -> str:
        """문자열 표현"""
        stats = self.get_stats()
        return f"LRUCache(size={len(self)}/{self.max_size}, hit_ratio={stats.hit_ratio:.1f}%)"


# 싱글톤 인스턴스 (애플리케이션 전역 캐시)
_default_cache: Optional[LRUCache] = None

def get_cache() -> LRUCache:
    """
    기본 LRU 캐시 인스턴스 반환 (싱글톤)
    
    Returns:
        LRUCache 인스턴스
    
    Examples:
        >>> cache = get_cache()
        >>> embedding = [0.1] * 1536
        >>> cache.set("key123", embedding)
        >>> cached = cache.get("key123")
    """
    global _default_cache
    if _default_cache is None:
        _default_cache = LRUCache(max_size=5000)
    return _default_cache

def reset_cache() -> None:
    """
    기본 캐시 인스턴스 초기화 (테스트 목적)
    """
    global _default_cache
    _default_cache = None
