---
description: "Phase 7 빠른 시작 가이드: Docker 배포 및 성능 테스트"
date: "2026-03-03"
---

# QA Chat Phase 7 빠른 시작 가이드

**목표**: Docker로 QA Chat을 배포하고 성능 테스트를 실행하기 (10분)

---

## 1. 필수 조건

### 설치 확인

```bash
# Docker 확인
docker --version
# 출력 예: Docker version 24.0.0

# Docker Compose 확인
docker-compose --version
# 출력 예: Docker Compose version 2.20.0

# Python (로컬 테스트용)
python --version
# 출력 예: Python 3.12.0
```

### 미설치 시
- **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop) 설치
- **Linux**: `sudo apt install docker.io docker-compose`

---

## 2. Docker로 실행 (3단계, 2분)

### Step 1: 이미지 빌드

```bash
# 프로젝트 루트에서
docker build -t qa-chat:latest .

# 출력:
# Step 1/15 : FROM python:3.12-slim
# ...
# Successfully built abc123...
# Successfully tagged qa-chat:latest
```

**소요 시간**: ~1분 (처음), ~10초 (캐시)

### Step 2: 컨테이너 실행

```bash
# 방법 A: 직접 docker 명령어
docker run -p 7860:7860 \
  -v $(pwd)/data:/app/data \
  -e ADMIN_PASSWORD=1234 \
  qa-chat:latest

# 방법 B: docker-compose 사용 (권장)
docker-compose up -d

# 방법 C (Windows PowerShell): 
docker run -p 7860:7860 `
  -v ${pwd}/data:/app/data `
  -e ADMIN_PASSWORD=1234 `
  qa-chat:latest
```

**출력**:
```
Application started
Running on http://0.0.0.0:7860
```

### Step 3: 상태 확인

```bash
# 방법 A: docker (직접 실행)
docker ps
# 또는
docker logs qa-chat  # 컨테이너 이름으로 로그 확인

# 방법 B: docker-compose 사용
docker-compose ps
docker-compose logs -f

# 웹 브라우저에서 테스트
# http://localhost:7860 열기 → Gradio UI 보이면 성공 ✅
```

---

## 3. 성능 테스트 (선택)

### 3.1 부하 테스트 (10명 동시 사용자)

```bash
# 1. Locust 설치
pip install locust==2.15.0

# 2. 테스트 파일 생성 (tests/performance/locustfile.py)
# (아래 샘플 코드 참조)

# 3. 테스트 실행
locust -f tests/performance/locustfile.py \
  --host=http://localhost:7860 \
  --users=10 \
  --spawn-rate=2 \
  --run-time=60s

# 4. 결과 해석
# Requests/sec: 초당 요청 수
# Response time (50%ile): 중앙값 응답 시간
# Failure ratio: 실패율 (0% 이상적)
```

### Locust 샘플 코드

```python
# tests/performance/locustfile.py

from locust import HttpUser, task, between, events
import random
import time

# 테스트 질문 샘플
QUESTIONS = [
    "Python이 뭐야?",
    "Docker는 뭐야?",
    "Chrome이 뭐야?",
    "임베딩이 뭐야?",
    "QA 시스템이 뭐야?",
]

class QAChatUser(HttpUser):
    """사용자 시뮬레이션"""
    
    wait_time = between(1, 3)  # 요청 사이 1-3초 대기
    
    @task(4)
    def search_answer(self):
        """사용자 검색 (80% 비율)"""
        question = random.choice(QUESTIONS)
        self.client.post("/run/search_answer", json={"data": [question]})
    
    @task(1)
    def admin_login(self):
        """관리자 로그인 (20% 비율)"""
        self.client.post("/run/admin_login", json={"data": ["1234"]})

# 테스트 진행률 이벤트 처리
@events.test_stop.add_listener
def on_test_stop(runner, **kwargs):
    print("\n=== Performance Test Results ===")
    print(f"Total requests: {runner.stats.total.num_requests}")
    print(f"Failed requests: {runner.stats.total.num_failures}")
    print(f"Average response time: {runner.stats.total.avg_response_time:.0f}ms")
    print(f"Max response time: {runner.stats.total.max_response_time:.0f}ms")
```

### 3.2 응답 시간 측정

```bash
# curl로 단일 요청 시간 측정
time curl -X POST http://localhost:7860/run/search_answer \
  -H "Content-Type: application/json" \
  -d '{"data": ["테스트 질문"]}'

# 출력:
# real 0m0.123s   # 실제 소요 시간
# user 0m0.004s
# sys  0m0.008s
```

### 3.3 메모리 및 CPU 모니터링

```bash
# 방법 A: docker stats (진행 중 모니터링)
docker stats qa-chat  # Ctrl+C로 종료

# 출력:
# CONTAINER  CPU %   MEM USAGE / LIMIT
# qa-chat    2.5%    120MiB / 512MiB

# 방법 B: 단일 스냅샷
docker stats --no-stream qa-chat
```

### 3.4 캐시 통계 확인

```bash
# Gradio의 데이터 끝점 확인
curl http://localhost:7860/api/predict

# 또는 관리자 API (구현 시 사용 가능)
curl http://localhost:7860/api/cache-stats
```

---

## 4. 문제 해결

### 포트 충돌

```bash
# ❌ 오류: "address already in use"

# 해결 방법 1: 포트 변경
docker run -p 7861:7860 qa-chat:latest
# http://localhost:7861 로 접근

# 해결 방법 2: 기존 컨테이너 중지
docker-compose down
docker ps
docker stop <container-id>
```

### 메모리 부족

```bash
# ❌ 오류: "Out of memory"

# 해결 방법: 메모리 한계 증가
docker run -m 1g qa-chat:latest  # 1GB로 설정

# docker-compose에서:
deploy:
  resources:
    limits:
      memory: 1G
```

### 데이터 지속성 문제

```bash
# ❌ 컨테이너 재시작 후 데이터 손실

# 확인: 볼륨 마운트 확인
docker inspect qa-chat | grep -i volumes

# 재설정: 볼륨 마운트 추가
docker run -v $(pwd)/data:/app/data qa-chat:latest
```

### 헬스 체크 실패

```bash
# ❌ "Health status: unhealthy"

# 해결 방법
docker logs qa-chat  # 로그 확인
docker exec qa-chat python -c "import requests; requests.get('http://localhost:7860/info')"
```

---

## 5. 개발 모드 (선택)

### 코드 .hot reloading (개발용)

```yaml
# docker-compose-dev.yml
version: "3.9"

services:
  qa-chat:
    build:
      context: .
      dockerfile: Dockerfile.dev  # 개발용 Dockerfile
    volumes:
      - .:/app  # 전체 프로젝트 마운트
      - /app/__pycache__  # 캐시 제외
    environment:
      - DEBUG=True
      - PYTHONUNBUFFERED=1
    ports:
      - "7860:7860"
```

```bash
# 개발 모드로 실행
docker-compose -f docker-compose-dev.yml up

# 코드 변경 후 자동 리로드됨
```

---

## 6. 프로덕션 체크리스트

배포 전 확인 사항:

```bash
# 1. 이미지 빌드
docker build -t qa-chat:1.0.0 .

# 2. 이미지 스캔 (보안)
docker scan qa-chat:1.0.0

# 3. 로컬 테스트
docker run -p 7860:7860 qa-chat:1.0.0

# 4. 부하 테스트 (10+ 사용자)
locust -f tests/performance/locustfile.py \
  --host=http://localhost:7860 \
  --users=10 \
  --run-time=300s

# 5. 성능 검증
✅ 평균 응답 시간 <100ms
✅ 캐시 히트율 >80%
✅ CPU <50%, 메모리 <400MB
✅ 실패율 0%

# 6. 데이터 지속성 테스트
docker-compose down
docker-compose up
# data/init.txt 여전히 있는지 확인

# 7. 환경 변수 설정
✅ ADMIN_PASSWORD 변경 (1234 아님)
✅ SIMILARITY_THRESHOLD 최적값 (0.7)
✅ 필요시 LANGFUSE_KEY 설정

# 8. 로그 전석 설정
✅ 로그 드라이버 구성 (크기 제한)
✅ 중앙 로깅 설정 (선택)
```

---

## 7. 다음 단계

### Phase 2 구현

```bash
# 캐시 서비스 구현 확인
docker exec qa-chat python -c "from src.services.cache_service import CacheService; print('✅ Cache service ready')"

# 성능 메트릭 확인
docker logs qa-chat | grep -i "cache\|performance"

# 회귀 테스트 (기존 94개 테스트)
docker exec qa-chat pytest tests/ -v --tb=short
```

### 모니터링 & 관찰성

```bash
# Langfuse 통합 확인
curl http://localhost:7860/api/metrics

# 성능 대시보드 설정 (선택)
# → Grafana 또는 DataDog 통합
```

---

## 8. 빠른 참조

| 작업 | 명령어 |
|------|--------|
| **빌드** | `docker build -t qa-chat:latest .` |
| **실행** | `docker-compose up -d` |
| **로그** | `docker-compose logs -f` |
| **중지** | `docker-compose down` |
| **상태** | `docker-compose ps` |
| **테스트** | `docker exec qa-chat pytest tests/` |
| **부하테스트** | `locust -f tests/performance/locustfile.py --host=http://localhost:7860 --users=10` |
| **메모리** | `docker stats qa-chat` |
| **삭제** | `docker system prune -a` |

---

## 9. 지원

문제 발생 시:

1. **로그 확인**: `docker-compose logs qa-chat`
2. **상태 확인**: `docker-compose ps`
3. **컨테이너 재시작**: `docker-compose restart`
4. **캐시 정리**: `docker system prune`
5. **문서 확인**: Phase 1 contracts/ 참조

---

**완성**: Phase 7 Phase 1 설계 완료 ✅  
**다음**: Phase 2 구현 (캐시, Docker, 테스트)
