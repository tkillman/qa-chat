---
description: "Phase 1 계약: 캐시 서비스 인터페이스"
date: "2026-03-03"
phase: "1"
---

# Cache Service Contract

## 목적
캐시 서비스의 공용 인터페이스를 정의합니다.
이 계약은 Phase 2에서 `CacheService` 구현을 위한 기준입니다.

---

## ICacheService 인터페이스

```python
# src/services/cache_service.py

from typing import Protocol, Optional, List
from src.models.cache_models import CacheStats

class ICacheService(Protocol):
    """
    캐시 서비스 인터페이스
    
    임베딩 결과를 메모리에 LRU 캐시로 저장하여 성능 최적화
    """
    
    def get(self, key: str) -> Optional[List[float]]:
        """
        캐시에서 임베딩 조회
        
        Args:
            key: 질문 텍스트의 SHA256 해시
        
        Returns:
            임베딩 벡터 (List[float]) 또는 None (캐시 미스)
        
        Raises:
            ValueError: 잘못된 키 형식
        
        Performance:
            - Hit: <1ms
            - Miss: 0ms (데이터 접근만)
        
        Examples:
            >>> cache_service.get("abc123...")
            [0.1, 0.2, ..., 0.5]  # 1536개 요소
            
            >>> cache_service.get("xyz789...")
            None  # 캐시 미스
        """
        ...
    
    def set(self, key: str, embedding: List[float]) -> None:
        """
        캐시에 임베딩 저장
        
        캐시가 가득 차면 LRU 정책에 따라 가장 오래된 항목 제거
        
        Args:
            key: 질문 텍스트의 SHA256 해시
            embedding: 임베딩 벡터 (List[float], 1536개)
        
        Returns:
            None
        
        Raises:
            ValueError: 임베딩 크기 불일치 (1536 필수)
            ValueError: 키 형식 오류
        
        Performance:
            - Normal: <1ms
            - With eviction: <2ms
        
        Examples:
            >>> embedding = [0.1] * 1536
            >>> cache_service.set("abc123...", embedding)
            
            >>> cache_service.get("abc123...")
            [0.1] * 1536  # 저장됨
        """
        ...
    
    def clear(self) -> None:
        """
        전체 캐시 초기화
        
        Returns:
            None
        
        Performance:
            <1ms
        
        Usage:
            관리자가 새 Q&A 배치를 업로드할 때 호출
            (임베딩 모델 변경 시)
        
        Examples:
            >>> cache_service.get_stats().cache_size
            1000
            >>> cache_service.clear()
            >>> cache_service.get_stats().cache_size
            0
        """
        ...
    
    def get_stats(self) -> CacheStats:
        """
        캐시 통계 조회
        
        Returns:
            CacheStats 객체:
            - total_requests: 전체 조회 요청 수
            - cache_hits: 캐시 히트 수
            - cache_misses: 캐시 미스 수
            - avg_response_time_ms: 평균 응답 시간
            - cache_size: 현재 캐시 크기
            - max_cache_size: 최대 캐시 크기
            - memory_used_mb: 메모리 사용량
        
        Performance:
            <1ms
        
        Examples:
            >>> stats = cache_service.get_stats()
            >>> print(stats.hit_ratio)
            85.5  # 85.5% 히트율
            >>> print(stats.to_dict())
            {
                "total_requests": 1000,
                "cache_hits": 855,
                "cache_misses": 145,
                "hit_ratio_percent": 85.5,
                ...
            }
        """
        ...
```

---

## 구현 요구사항

### 메모리 관리
- **최대 크기**: 5000개 항목 (초기값, 구성 가능)
- **메모리 대상**: <512MB (Docker 컨테이너)
- **LRU 정책**: 마지막 접근 시간 기준 최오래된 항목 제거

### 스레드 안전성
- **동시 접근**: Gradio는 스레드 풀(20)로 다중 요청 처리
- **요구사항**: `thread-safe` 또는 GIL 활용 충분
- **구현**: Python `threading.Lock` 또는 `OrderedDict` (GIL 보호)

### 오류 처리
```python
# 허용되는 오류 상황
try:
    cache_service.get(invalid_key)
except ValueError:
    pass  # 예상된 오류

try:
    cache_service.set(key, wrong_size_embedding)
except ValueError:
    pass  # 예상된 오류
```

### 계약 검증 (단위 테스트)

```python
# tests/contracts/test_cache_contract.py

def test_cache_get_hit():
    """캐시 히트 테스트"""
    cache_service = CacheService()
    embedding = [0.1] * 1536
    
    cache_service.set("key1", embedding)
    result = cache_service.get("key1")
    
    assert result == embedding
    assert cache_service.get_stats().cache_hits == 1

def test_cache_lru_eviction():
    """LRU 제거 테스트"""
    cache_service = CacheService(max_size=2)
    
    cache_service.set("key1", [0.1] * 1536)
    cache_service.set("key2", [0.2] * 1536)
    cache_service.set("key3", [0.3] * 1536)  # key1 제거됨
    
    assert cache_service.get("key1") is None  # 제거됨
    assert cache_service.get("key2") is not None
    assert cache_service.get("key3") is not None

def test_thread_safety():
    """스레드 안전성 테스트"""
    # 20개 스레드에서 동시에 get/set 수행
    # 모든 요청 완료되고 통계 일관성 검증
    ...
```

---

## 통합 지점

### EmbeddingService와의 연계

```python
# src/services/embedding_service.py 수정 계획

class EmbeddingService:
    def __init__(self, cache_service: ICacheService):
        self.cache = cache_service
        self.llm = openai.Embedding(...)  # 또는 다른 LLM
    
    def get_embedding(self, question: str) -> List[float]:
        """캐시 확인 후 임베딩 생성"""
        # 1. 캐시 확인
        cached = self.cache.get(self._hash_question(question))
        if cached:
            return cached
        
        # 2. 캐시 미스: LLM 호출
        embedding = self.llm.embed(question)
        
        # 3. 캐시 저장
        self.cache.set(self._hash_question(question), embedding)
        
        return embedding
    
    @staticmethod
    def _hash_question(question: str) -> str:
        return hashlib.sha256(question.strip().lower().encode()).hexdigest()
```

### main.py에서의 사용

```python
# src/main.py

from src.services.cache_service import CacheService
from src.services.embedding_service import EmbeddingService

# 초기화
cache_service = CacheService(max_size=5000)
embedding_service = EmbeddingService(cache_service)

# 사용자 검색 시 (캐시가 투명하게 사용됨)
results = embedding_service.get_embedding(user_question)
```

---

## 모니터링 & Langfuse 통합

```python
# src/services/langfuse_service.py 확장

def log_cache_access(self, hit: bool, response_time_ms: float):
    """캐시 접근 기록"""
    trace.event(
        name="cache_access",
        metadata={
            "hit": hit,
            "response_time_ms": response_time_ms
        }
    )

def log_cache_stats(self, stats: CacheStats):
    """캐시 통계 기록"""
    trace.event(
        name="cache_stats",
        metadata=stats.to_dict()
    )
```

---

## 성공 기준

### 기능 검증
- ✅ get/set/clear 모두 동작
- ✅ LRU 제거 정책 작동
- ✅ 스레드 안전
- ✅ 통계 정확성

### 성능 검증
- ✅ 캐시 히트: <1ms
- ✅ 캐시 미스: <2ms (제거 포함)
- ✅ 메모리 <512MB (5000개 항목)
- ✅ 에너지 효율 (CPU 사용량 <5% idle)

### 부하 테스트
- ✅ 10 동시 사용자 (locust)
- ✅ 평균 응답 <100ms
- ✅ 히트율 80% 이상

---

## 참고: TypeScript/Go 대체 구현

이 계약은 언어 무관하며, 다음 경우 활용 가능:

### TypeScript (Node.js)
```typescript
interface ICacheService {
    get(key: string): Promise<number[] | null>;
    set(key: string, embedding: number[]): Promise<void>;
    clear(): Promise<void>;
    getStats(): Promise<CacheStats>;
}
```

### Go
```go
type ICacheService interface {
    Get(key string) ([]float32, error)
    Set(key string, embedding []float32) error
    Clear() error
    GetStats() CacheStats
}
```

---

**계약 작성 완료**: Phase 1 부분 2/4  
**다음**: contracts/docker_contract.py (Docker 팩토리 정의)
