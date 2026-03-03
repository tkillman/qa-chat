---
description: "Phase 7 연구: 성능 최적화 및 Docker 배포 기술"
date: "2026-03-03"
phase: "0"
---

# Phase 0 Research: 성능 최적화 및 Docker 배포

## 1. 캐싱 전략 연구

### 1.1 LRU (Least Recently Used) 캐시

**선택 이유**: 임베딩 생성은 비용이 높고(LLM 호출), 반복 질문이 많기 때문에 캐시의 효과가 크다.

#### 구현 방식
- **기술**: Python `functools.lru_cache` 또는 직접 구현
- **Key**: 질문 텍스트의 해시 (MD5 또는 SHA256)
- **Value**: 임베딩 벡터 (List[float])
- **메모리**: N개 캐시 × 1536차원(기본 임베딩) × 4bytes = ~6MB per 1000 items

#### 성능 예상
- 캐시 히트: 임베딩 생성 건너뜀 → <1ms 응답
- 캐시 미스: 임베딩 생성 필요 → ~500ms 응답
- 히트율 추정: 80% (반복 질문 가정) → 평균 100ms

#### 캐시 무효화
- **수동 무효화**: 관리자가 새 Q&A 추가 시
- **TTL 미지원**: 벡터는 학습 기반이므로 시간 기반 만료 불필요
- **LRU 제한**: 최대 5000개 항목 (메모리 ~30MB)

### 1.2 대안 검토

| 옵션 | 장점 | 단점 | 결정 |
|------|------|------|------|
| **LRU 메모리** | 빠름, 간단 | 단일 인스턴스 전용 | ✅ 선택 |
| **Redis** | 다중 인스턴스 공유 | 복잡도 ↑, 외부 의존 | ❌ MVP 외 |
| **파일 캐시** | 지속성 | 느림, 동기화 어려움 | ❌ MVP 외 |
| **DB 캐시** | ChromaDB와 통합 | 중복성, 복잡도 | ❌ MVP 외 |

### 1.3 구현 계획
```python
# 캐시 서비스 (메모리 기반)
class LRUCache:
    def __init__(self, max_size=5000):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[List[float]]:
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def put(self, key: str, value: List[float]):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
    
    def get_stats(self):
        return {"hits": self.hits, "misses": self.misses, "hit_ratio": ...}
```

---

## 2. Gradio 비동기 처리 연구

### 2.1 현황 분석
- Gradio 4.26.0+는 **기본적으로 비동기 지원** (async def 함수 사용 가능)
- 현재 main.py의 함수들이 동기식(정상 def)이므로 개선 여지 있음

### 2.2 비동기 개선 시나리오
```python
# 현재 (동기식)
def search_answer(question: str):
    embedding = embedding_service.get_embedding(question)  # 500ms 대기
    results = chromadb_service.search(embedding)  # 100ms 대기
    return results  # 총 600ms

# 개선 후 (비동기)
async def search_answer(question: str):
    # 병렬 처리 불가 (순차적 의존성) 이므로 async/await 이점 제한
    # 하지만 I/O 대기 중 다른 요청 처리 가능
    embedding = await embedding_service.get_embedding_async(question)
    results = await chromadb_service.search_async(embedding)
    return results
```

### 2.3 Gradio 스레드 풀 최적화
- Gradio 기본: 스레드 풀 크기 = 10
- 권장 크기: 동시 사용자 수 × 2 = 10 × 2 = 20
- 설정: `gr.Interface(..., server_name="0.0.0.0", server_port=7860, concurrency_limit=20)`

### 2.4 결정
- ✅ 비동기/동기 혼합 지원 (기존 코드 유지)
- ✅ Gradio 스레드 풀 설정 (20으로 증대)
- ⏳ 전체 비동기 마이그레이션은 Phase 7 외 (복잡도 높음)

---

## 3. Docker 배포 연구

### 3.1 기본 이미지 선택

| 이미지 | 크기 | 빌드 시간 | 보안 | 선택 |
|--------|------|---------|------|------|
| **python:3.12-slim** | ~150MB | 빠름 | 양호 | ✅ 선택 |
| **python:3.12-alpine** | ~50MB | 매우 빠름 | 우수 | ⏳ 나중에 |
| **python:3.12** | ~1GB | 느림 | 양호 | ❌ 제외 |
| **ubuntu + python** | ~1GB | 느림 | 양호 | ❌ 제외 |

### 3.2 멀티 스테이지 빌드
```dockerfile
# Stage 1: 빌드
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: 런타임
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["python", "src/main.py"]
```

**효과**: 최종 이미지 ~200MB (필수 파일만 포함)

### 3.3 환경 변수 관리
```dockerfile
# Dockerfile에서 기본값 설정
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
```

### 3.4 헬스 체크
```dockerfile
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:7860/info')"
```

### 3.5 docker-compose.yml 구성
```yaml
version: "3.9"

services:
  qa-chat:
    build: .
    ports:
      - "7860:7860"
    environment:
      - ADMIN_PASSWORD=1234
      - SIMILARITY_THRESHOLD=0.7
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:7860/info')"]
      interval: 10s
      timeout: 3s
      retries: 3
```

**효과**: 단일 명령으로 실행: `docker-compose up`

---

## 4. 성능 테스트 도구

### 4.1 Tool 선택

| 도구 | 목적 | 사용 대상 |
|------|------|---------|
| **locust** | 부하 테스트 | 동시 10+ 사용자 시뮬레이션 |
| **pytest-benchmark** | 성능 측정 | 개별 함수 응답 시간 |
| **docker stats** | 리소스 모니터링 | CPU, 메모리 사용량 |
| **pytest-xdist** | 병렬 테스트 | 회귀 테스트 가속화 |

### 4.2 Locust 설정 (부하 테스트)

```python
from locust import HttpUser, task, between

class QAChatUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(1)
    def search_question(self):
        """사용자 질문 시뮬레이션"""
        self.client.post("/api/search", json={"question": "테스트 질문"})
    
    @task(3)
    def admin_login(self):
        """로그인 이벤트 (비율 낮음)"""
        self.client.post("/api/login", json={"password": "1234"})

# 실행: locust -f locustfile.py --host=http://localhost:7860 --users=10 --spawn-rate=2
```

**기대 결과**: 10명 동시 사용자, 평균 응답 시간 <200ms

### 4.3 pytest-benchmark 설정

```python
def test_embedding_generation_benchmark(benchmark):
    result = benchmark(embedding_service.get_embedding, "테스트 질문")
    assert len(result) == 1536  # 임베딩 차원

# 실행: pytest tests/performance/ --benchmark-compare
```

**기대 결과**: 첫 요청 ~500ms, 캐시 히트 <1ms

---

## 5. 동시성 처리 전략

### 5.1 Gradio + Python asyncio 조합

```python
import asyncio
from gradio import Interface

async def search_async(question: str):
    """비동기 검색"""
    try:
        # 타임아웃 설정 (10초)
        embedding = await asyncio.wait_for(
            asyncio.to_thread(embedding_service.get_embedding, question),
            timeout=10
        )
        results = await asyncio.wait_for(
            asyncio.to_thread(chromadb_service.search, embedding),
            timeout=10
        )
        return results
    except asyncio.TimeoutError:
        return "응답 시간 초과"

# Gradio는 이 함수를 자동으로 비동기 처리
interface = Interface(fn=search_async, inputs="text", outputs="text")
```

### 5.2 스레드 풀 설정
```python
# src/main.py에서
gr.Interface(
    fn=search_answer,
    inputs="text",
    outputs="text",
    server_name="0.0.0.0",
    server_port=7860,
    concurrency_limit=20,  # 동시 20개 요청 처리
)
```

### 5.3 요청 큐 관리
- Gradio가 자동으로 요청 큐 관리합니다
- 최대 큐 크기: `queue_size=100` (설정 가능)

---

## 6. 종합 결정 사항

### Phase 7 기술 스택

| 요소 | 선택 | 사유 |
|------|------|------|
| **캐시** | LRU (메모리) | 빠름, 간단, MVP 적합 |
| **비동기** | Gradio 기본 + 스레드 풀 20 | 최소 개입, 안정성 |
| **Docker 이미지** | python:3.12-slim | 150MB, 빠른 빌드 |
| **부하 테스트** | locust | 10+ 사용자 검증 |
| **성능 측정** | pytest-benchmark | 응답 시간 추적 |

### 성능 목표 검증

- **목표**: 동시 10+ 사용자, 평균 응답 <100ms
- **예상 결과** (캐시 80% 히트율):
  - 캐시 히트: <1ms
  - 캐시 미스: ~500ms
  - 평균: 0.8 × 1 + 0.2 × 500 = ~101ms ✅
  - 10명 동시 처리: 스레드 풀 20 충분 ✅

### Phase 1 설계 입력
- ✅ 캐시 데이터 모델 (CacheEntry, CacheStats)
- ✅ 캐시 서비스 인터페이스 (get/set/stats)
- ✅ Docker Compose 구조
- ✅ Locust 부하 테스트 구조

---

## 7. 다음 단계 (Phase 1)

1. **data-model.md**: CacheEntry, CacheStats 정의
2. **contracts/cache_contract.py**: ICacheService 프로토콜
3. **contracts/docker_contract.py**: Docker 팩토리 패턴
4. **quickstart.md**: Docker 실행 및 테스트 방법

---

**시간 추정**: 연구 완료 (1-2시간) ✅
**다음 명령**: Phase 1 설계로 진행
