"""Cache models for Phase 7 performance optimization."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import hashlib


@dataclass
class CacheEntry:
    """
    캐시에 저장되는 개별 임베딩 항목
    
    Attributes:
        key: 질문 텍스트의 SHA256 해시 (캐시 키)
        embedding: 임베딩 벡터 (List[float], 1536차원)
        created_at: 캐시 항목 생성 시간
        access_count: 캐시 히트 횟수
        last_accessed: 마지막 접근 시간 (LRU 순서 판정용)
        question_text: 원본 질문 (통계용, 선택)
    """
    
    key: str                              # SHA256 해시
    embedding: List[float]                # 임베딩 벡터
    created_at: datetime                  # 생성 시간
    access_count: int = 0                 # 캐시 히트 카운트
    last_accessed: Optional[datetime] = None  # 마지막 접근 시간
    question_text: Optional[str] = None   # 원본 질문 (옵션)
    
    def __post_init__(self):
        """검증 및 초기화"""
        if not isinstance(self.embedding, list) or len(self.embedding) != 1536:
            raise ValueError(f"Embedding must be list of 1536 floats, got {len(self.embedding)}")
        if len(self.key) != 64:  # SHA256 hex length
            raise ValueError(f"Key must be SHA256 hash (64 chars), got {len(self.key)}")
    
    @classmethod
    def from_question(cls, question: str, embedding: List[float]) -> 'CacheEntry':
        """질문과 임베딩으로부터 CacheEntry 생성"""
        key = hashlib.sha256(question.strip().lower().encode()).hexdigest()
        return cls(
            key=key,
            embedding=embedding,
            created_at=datetime.utcnow(),
            question_text=question
        )
    
    def record_access(self):
        """접근 기록 (히트 증가)"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """직렬화"""
        return {
            "key": self.key,
            "embedding": self.embedding,
            "created_at": self.created_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "question_text": self.question_text,
        }


@dataclass
class CacheStats:
    """
    캐시 성능 통계
    
    Attributes:
        total_requests: 전체 조회 요청 수
        cache_hits: 캐시 히트 수
        cache_misses: 캐시 미스 수
        avg_response_time_ms: 평균 응답 시간 (ms)
        cache_size: 캐시에 저장된 항목 수
        max_cache_size: 최대 캐시 크기
        memory_used_mb: 사용 중인 메모리 (MB)
    """
    
    total_requests: int = 0               # 전체 요청
    cache_hits: int = 0                   # 캐시 히트
    cache_misses: int = 0                 # 캐시 미스
    avg_response_time_ms: float = 0.0     # 평균 응답 시간
    cache_size: int = 0                   # 현재 캐시 크기
    max_cache_size: int = 5000            # 최대 캐시 크기
    memory_used_mb: float = 0.0           # 메모리 사용량
    
    @property
    def hit_ratio(self) -> float:
        """캐시 히트율 (%)"""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100
    
    @property
    def miss_ratio(self) -> float:
        """캐시 미스율 (%)"""
        return 100 - self.hit_ratio
    
    def to_dict(self) -> dict:
        """직렬화"""
        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_ratio_percent": round(self.hit_ratio, 2),
            "miss_ratio_percent": round(self.miss_ratio, 2),
            "avg_response_time_ms": round(self.avg_response_time_ms, 2),
            "cache_size": self.cache_size,
            "max_cache_size": self.max_cache_size,
            "memory_used_mb": round(self.memory_used_mb, 2),
        }
    
    def to_string(self) -> str:
        """문자열 표현"""
        return f"""
Cache Statistics:
- Requests: {self.total_requests} (Hits: {self.cache_hits}, Misses: {self.cache_misses})
- Hit Ratio: {self.hit_ratio:.1f}%
- Avg Response Time: {self.avg_response_time_ms:.1f}ms
- Cache Size: {self.cache_size}/{self.max_cache_size}
- Memory Used: {self.memory_used_mb:.1f}MB
"""
