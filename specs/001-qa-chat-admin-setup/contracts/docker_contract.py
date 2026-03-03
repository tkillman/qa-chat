---
description: "Phase 1 계약: Docker 배포 팩토리"
date: "2026-03-03"
phase: "1"
---

# Docker Deployment Contract

## 목적
Docker 컨테이너화 및 배포를 위한 표준 정의합니다.
Phase 2에서 Dockerfile 및 docker-compose.yml 구현을 위한 기준입니다.

---

## Dockerfile 요구사항

### 이미지 구성

```dockerfile
# Stage 1: 빌드 (필요한 패키지 설치)
FROM python:3.12-slim as builder
WORKDIR /build

# 의존성 파일 복사
COPY requirements.txt .

# 패키지 설치 (사용자 디렉토리로)
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: 런타임 (최소 이미지)
FROM python:3.12-slim
WORKDIR /app

# 빌드 스테이지에서 설치된 패키지 복사
COPY --from=builder /root/.local /root/.local

# 애플리케이션 코드 복사
COPY . .

# Python 경로 설정
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Gradio 서버 설정
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860
ENV GRADIO_ANALYTICS_ENABLED=False

# 헬스 체크
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/info')" || exit 1

# 진입점
CMD ["python", "src/main.py"]
```

### 이미지 특성
- **베이스 이미지**: `python:3.12-slim`
- **최종 크기**: ~200MB (멀티 스테이지 빌드)
- **보안**: 시스템 패키지 최소화, root 사용자
- **빌드 시간**: <2분 (변경사항 없을 때)

### 환경 변수

```dockerfile
# 필수 환경 변수
GRADIO_SERVER_NAME=0.0.0.0          # 외부 접근 가능
GRADIO_SERVER_PORT=7860             # 포트 (변경 가능)
ADMIN_PASSWORD=1234                 # 기본값 (보안: 외부화 필요)
SIMILARITY_THRESHOLD=0.7            # 유사도 임계값

# 선택 환경 변수
CACHE_MAX_SIZE=5000                 # 캐시 최대 크기
LANGFUSE_PUBLIC_KEY=...             # Langfuse 통합 (선택)
LANGFUSE_SECRET_KEY=...             # Langfuse 통합 (선택)

# Python 최적화
PYTHONUNBUFFERED=1                  # 버퍼링 비활성화 (즉시 출력)
PYTHONDONTWRITEBYTECODE=1           # .pyc 파일 생성 안 함
```

---

## docker-compose.yml 요구사항

### 기본 구성

```yaml
version: "3.9"

services:
  qa-chat:
    # 빌드 또는 이미지 지정
    build:
      context: .
      dockerfile: Dockerfile
    
    # 이미지 태그
    image: qa-chat:latest
    
    # 포트 매핑
    ports:
      - "7860:7860"
    
    # 환경 변수
    environment:
      - ADMIN_PASSWORD=1234
      - SIMILARITY_THRESHOLD=0.7
      - CACHE_MAX_SIZE=5000
      - GRADIO_SERVER_NAME=0.0.0.0
      - GRADIO_SERVER_PORT=7860
    
    # 볼륨 마운트 (데이터 지속성)
    volumes:
      - ./data:/app/data
    
    # 헬스 체크
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:7860/info')"]
      interval: 10s
      timeout: 3s
      start_period: 5s
      retries: 3
    
    # 리소스 제한
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'
        reservations:
          memory: 256M
          cpus: '0.5'
    
    # 재시작 정책
    restart: unless-stopped
    
    # 로그 드라이버
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # (선택) Nginx 리버스 프록시
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - qa-chat
    restart: unless-stopped
```

### 환경변수 관리

```yaml
# Option 1: .env 파일 사용
env_file:
  - .env

# Option 2: 중복 환경에 따라
version: "3.9"
services:
  qa-chat:
    environment:
      - ADMIN_PASSWORD=${ADMIN_PASSWORD:-1234}  # 기본값 제공
      - SIMILARITY_THRESHOLD=${SIMILARITY_THRESHOLD:-0.7}
```

---

## Docker 빌드 & 실행 계약

### 빌드

```bash
# 로컬 빌드
docker build -t qa-chat:latest .

# 빌드 및 실행 (docker-compose)
docker-compose up --build

# 빌드 캐시 무시
docker build -t qa-chat:latest . --no-cache
```

### 실행

```bash
# Docker 직접 실행
docker run -p 7860:7860 \
  -e ADMIN_PASSWORD=1234 \
  -v $(pwd)/data:/app/data \
  qa-chat:latest

# Docker Compose로 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f qa-chat

# 중지
docker-compose down
```

### 패키지/의존성

```dockerfile
# requirements.txt에 포함되어야 할 항목
gradio==4.26.0+
chromadb==0.4.24+
langfuse==2.12.0+
python-dotenv==1.0.0+
requests==2.31.0+ (헬스 체크용)
pytest==7.4.3+
```

---

## 볼륨 관리

### 데이터 지속성

```yaml
volumes:
  # 로컬 디렉토리 마운트 (호스트와 공유)
  - ./data:/app/data

  # 명명된 볼륨 (Docker 관리)
  - app-data:/app/data
```

### 마운트 포인트 구조

```
/app/
├── data/                        # 데이터 지속성 (마운트)
│   ├── init.txt                 # Q&A 항목
│   └── .chroma/                 # ChromaDB 데이터
├── src/                         # 애플리케이션 코드
├── tests/                       # 테스트 (선택적)
├── requirements.txt             # 의존성
└── Dockerfile                   # 이 파일
```

---

## 보안 고려사항

### 1. 환경 변수 외부화
```dockerfile
# ❌ 나쁜 예: 하드코딩
ENV ADMIN_PASSWORD=1234

# ✅ 좋은 예: 런타임에 제공
docker run -e ADMIN_PASSWORD=<secure-password> qa-chat:latest
```

### 2. 루트 사용자 비활성화 (선택)
```dockerfile
# 선택: 비루트 사용자 생성
RUN useradd -m -u 1000 appuser
USER appuser
```

### 3. 파일 권한
```dockerfile
RUN chmod -R 755 /app
```

---

## 성능 최적화

### 이미지 크기
- **목표**: <200MB (멀티 스테이지 빌드)
- **검증**: `docker images qa-chat`

### 빌드 최적화
- Layer 캐싱: 자주 변경되지 않는 것부터 먼저
- 불필요한 파일 제외: `.dockerignore` 활용

### 런타임 최적화
```yaml
# 메모리 제한 (리소스 고정)
deploy:
  resources:
    limits:
      memory: 512M

# CPU 제한
deploy:
  resources:
    limits:
      cpus: '1.0'
```

---

## 헬스 체크 정의

```dockerfile
# Dockerfile에서
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/info')"

# 실행 결과: 성공 (exit 0) 또는 실패 (exit 1)
```

### 사용
```bash
# 헬스 상태 확인
docker ps --format "{{.Names}}: {{.Status}}"

# 출력 예:
# qa-chat: Up 5 minutes (healthy)
```

---

## 다중 인스턴스 배포 (고급)

### Compose 스케일링

```yaml
services:
  qa-chat:
    # ...
    deploy:
      replicas: 3  # 3개 인스턴스
```

```bash
# 또는 CLI에서
docker-compose up --scale qa-chat=3

# nginx가 로드 밸런싱합니다
```

---

## 통합 테스트 (Phase 2)

```bash
# 이미지 빌드
docker build -t qa-chat:test .

# 컨테이너 실행
docker run -d --name test-container \
  -p 7860:7860 \
  -e ADMIN_PASSWORD=1234 \
  qa-chat:test

# 헬스 체크
docker exec test-container curl http://localhost:7860/info

# 로그 확인
docker logs test-container

# 성능 테스트
locust -f tests/performance/locustfile.py \
  --host http://localhost:7860 \
  --users 10 \
  --spawn-rate 2
```

---

## 배포 환경별 설정

### 로컬 개발
```yaml
services:
  qa-chat:
    image: qa-chat:dev
    ports:
      - "7860:7860"
    volumes:
      - .:/app              # 코드 마운트 (핫 리로드)
      - ./data:/app/data
    environment:
      - DEBUG=True
```

### 스테이징 / 프로덕션
```yaml
services:
  qa-chat:
    image: qa-chat:1.0.0   # 버전 태그
    restart: always
    deploy:
      resources:
        limits:
          memory: 512M
    healthcheck:
      # ... 더 엄격한 조건
```

---

## 성공 기준

### 빌드
- ✅ `docker build` 성공 (<2분)
- ✅ 이미지 크기 <200MB
- ✅ 보안 스캔 통과 (docker scan)

### 실행
- ✅ `docker run` 시작 성공
- ✅ `http://localhost:7860` 접근 가능
- ✅ 헬스 체크 통과

### 배포
- ✅ `docker-compose up` 성공
- ✅ 데이터 지속성 (컨테이너 재시작 후 데이터 유지)
- ✅ 환경 변수 주입 동작
- ✅ 로그 출력 정상

---

**계약 작성 완료**: Phase 1 부분 3/4  
**다음**: quickstart.md (Docker 및 테스트 가이드)
