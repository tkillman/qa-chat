---
description: "Phase 1 데이터 모델: 캐시 엔티티 및 통계"
date: "2026-03-03"
phase: "1"
---

# Phase 1: 데이터 모델 설계

## 1. 캐시 데이터 모델

### 1.1 CacheEntry (캐시 항목)

**목적**: 임베딩 캐시에 저장되는 개별 항목

```python
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
```

### 1.2 CacheStats (캐시 통계)

**목적**: 캐시 성능 모니터링

```python
from dataclasses import dataclass
from typing import Optional

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
```

---

## 2. 관련 모델 정리

### 2.1 기존 QAItem 모델과의 관계

```python
# 기존 (src/models/qa_item.py)
@dataclass
class QAItem:
    question: str
    answer: str
    embedding: List[float]      # 임베딩 (캐시되지 않는 영구 저장소)
    metadata: dict = field(default_factory=dict)

# 신규 캐시 모델
CacheEntry:                     # 임베딩만 캐시 (빠른 조회용)
- key: 질문 해시
- embedding: 임베딩 벡터
- access_count/last_accessed: LRU 추적

# 관계:
# QAItem.embedding → CacheEntry로부터 복사 (캐시 미스 시)
# CacheEntry.embedding → ChromaDB 검색에 사용
```

### 2.2 저장소 구조

```
메모리 캐시 (LRU)
  ↓ (캐시 미스 시 역할)
ChromaDB 검색
  ↓ (첫 임베딩 생성 시 역할)
Embedding Service (LLM 호출)
  ↓ (결과 저장)
File Service (init.txt)
```

---

## 3. 캐시 모델 검증 기준

### 3.1 유효성 검사

```python
# test_cache_models.py 에서 검증할 항목들:

1. CacheEntry 생성
   - 올바른 임베딩 크기 (1536) 확인
   - SHA256 키 생성 확인
   - 타임스탬프 자동 생성 확인

2. CacheStats 계산
   - HitRatio = Hits / (Hits + Misses)
   - MissRatio = 1 - HitRatio
   - 초기값 확인 (0 또는 기본값)

3. 직렬화
   - to_dict() 모든 필드 포함 확인
   - to_string() 읽기 편한 형식 확인
```

### 3.2 성능 기준

```python
# 캐시 항목 메모리 계산:
- CacheEntry one item: ~6KB (메타데이터) + ~6MB (임베딩 벡터)
- 5000개 항목: ~30MB (허용범위 512MB 내)
- 직렬화/역직렬화: <1ms
```

---

## 4. Phase 2 구현 연계

### 4.1 캐시 서비스에서 사용

```python
# src/services/cache_service.py
from src.models.cache_models import CacheEntry, CacheStats

class CacheService:
    def __init__(self, max_size: int = 5000):
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = CacheStats(max_cache_size=max_size)
    
    def get_embedding(self, question: str) -> Optional[List[float]]:
        """캐시 조회"""
        key = hashlib.sha256(...)
        if key in self.cache:
            entry: CacheEntry = self.cache[key]
            entry.record_access()              # CacheEntry 메서드 사용
            self.stats.cache_hits += 1
            return entry.embedding
        
        self.stats.cache_misses += 1
        return None
    
    def set_embedding(self, question: str, embedding: List[float]):
        """캐시 저장"""
        entry = CacheEntry.from_question(question, embedding)  # CacheEntry 생성
        self.cache[entry.key] = entry
        self.stats.cache_size = len(self.cache)
    
    def get_stats(self) -> dict:
        """통계 조회"""
        return self.stats.to_dict()            # CacheStats 직렬화
```

### 4.2 테스트에서 사용

```python
# tests/unit/test_cache_models.py
def test_cache_entry_creation():
    embedding = [0.1] * 1536
    entry = CacheEntry.from_question("테스트", embedding)
    
    assert entry.question_text == "테스트"
    assert len(entry.embedding) == 1536
    assert entry.access_count == 0
    assert entry.last_accessed is None

def test_cache_stats_hit_ratio():
    stats = CacheStats()
    stats.total_requests = 100
    stats.cache_hits = 80
    stats.cache_misses = 20
    
    assert stats.hit_ratio == 80.0
    assert stats.miss_ratio == 20.0
```

---

## 5. 데이터 모델 파일 구조

### 5.1 파일 생성 계획

```python
# src/models/cache_models.py (신규)
- CacheEntry
- CacheStats
- 유틸리티 함수들

# 기존 파일 유지
src/models/qa_item.py
src/models/...
```

### 5.2 import 정리 (main.py에서)

```python
# 기존
from src.models.qa_item import QAItem

# 신규 추가
from src.models.cache_models import CacheEntry, CacheStats
from src.services.cache_service import CacheService
```

---

## 6. 다음 단계

- ✅ data-model.md 작성 (Phase 1 부분 1)
- → Phase 1 부분 2: contracts/cache_contract.py (캐시 서비스 인터페이스)
- → Phase 1 부분 3: contracts/docker_contract.py (Docker 팩토리)
- → Phase 1 부분 4: quickstart.md (Docker 및 성능 테스트 가이드)

**예상 시간**: 2-3시간 (설계 완료)
