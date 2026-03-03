# Implementation Plan: QA Chat Phase 7 - Polish & Deploy

**Branch**: `001-qa-chat-admin-setup` | **Date**: 2026-03-03 | **Spec**: [spec.md](spec.md)
**Input**: Phase 7 명확화 결과 (성능 최적화, Docker 배포, 동시 10+ 사용자)

**Note**: Phase 1-6 MVP 완료. Phase 7은 성능 최적화 및 배포 준비 단계입니다.

## Summary

**목표**: MVP (Phase 1-6) 기반으로 성능을 최적화하고 Docker 컨테이너 배포를 준비합니다.
- ✅ 기존 기능 유지 (US1-4 완료)
- 🚀 응답 시간 개선 (메모리 캐싱)
- 👥 동시 사용자 지원 (10+ 사용자)
- 🐳 Docker 배포 준비

**기술 접근**:
1. 임베딩 결과 메모리 캐싱 (LRU 캐시)
2. Gradio 비동기 처리 개선
3. Dockerfile + docker-compose.yml 작성
4. 부하 테스트 & 성능 검증

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: Gradio 4.26.0+, ChromaDB 0.4.24+, Docker, python-dotenv  
**Storage**: 파일 저장소 (init.txt, JSON) + ChromaDB 벡터 DB  
**Testing**: pytest (기존 유지), docker run (컨테이너 테스트)  
**Target Platform**: Linux/macOS/Windows (Docker 컨테이너)  
**Project Type**: Web application (Gradio UI + Python backend)  
**Performance Goals**: 동시 10+ 사용자 처리, 검색 응답 <100ms  
**Constraints**: 메모리 <512MB (컨테이너), 상태 없음 (stateless)  
**Scale/Scope**: 10K+ Q&A 항목 처리

### 현재 상태 (Phase 1-6)
- ✅ 94개 테스트 (모두 통과)
- ✅ 4개 사용자 스토리 구현
- ✅ Langfuse 추적 통합
- ⚠️ 단일 사용자 기준 설계
- ⚠️ Docker 미배포

### Phase 7 목표
- 🚀 부하 테스트 후 성능 개선
- 🐳 Docker 컨테이너화
- 👥 동시 사용자 지원 (목표: 10+)
- 📊 메모리 캐싱 추가

## Constitution Check

*GATE: Must pass before Phase 0 research.*

### 헌법 원칙 준수 확인

| 원칙 | 상태 | 설명 |
|-----|------|------|
| **TDD** | ✅ | 부하 테스트 & 성능 테스트 작성 후 최적화 |
| **UI는 Gradio** | ✅ | 기존 Gradio UI 유지 (비동기 개선만) |
| **관찰성 (Langfuse)** | ✅ | 성능 메트릭 추적 (응답 시간 로깅) |
| **상태 없음 (Stateless)** | ✅ | Docker 컨테이너 다중 인스턴스 지원 |
| **버전 관리** | ✅ | 기존 테스트 모두 통과 유지 |

### 추가 확인 사항

- ✅ **기존 기능 보존**: Phase 1-6 기능 유지, 회귀 테스트 필수
- ✅ **성능 목표 명확**: 동시 10+ 사용자 (현재 단일 기준)
- ✅ **배포 전략 확정**: Docker 컨테이너 (kubernetes 미지원)
- ✅ **데이터 구조 확정**: 파일 + ChromaDB 유지 (마이그레이션 미해당)

## Project Structure

### Documentation (Phase 7)

```text
specs/001-qa-chat-admin-setup/
├── plan.md              # 이 파일 (/speckit.plan 출력)
├── research.md          # Phase 0: 성능 최적화 연구
├── data-model.md        # Phase 1: 캐시 모델 설계
├── quickstart.md        # Phase 1: Docker 빠른 시작
├── contracts/           # Phase 1: 캐시 계약 테스트
└── tasks.md             # Phase 2: 작업 목록
```

### Source Code (기존 구조 + 신규)

```text
qa-chat/
├── src/
│   ├── models/
│   ├── services/
│   │   └── cache_service.py        # 🆕 메모리 캐시 서비스
│   ├── utils/
│   │   └── cache.py                # 🆕 LRU 캐시 구현
│   └── main.py                     # 수정: 비동기 개선
├── tests/
│   ├── unit/
│   │   └── test_cache_service.py   # 🆕 캐시 유닛 테스트
│   ├── integration/
│   │   └── test_cache_integration.py # 🆕 캐시 통합 테스트
│   └── performance/                 # 🆕 부하 테스트
│       ├── test_concurrent_users.py # 동시 사용자 테스트
│       └── test_response_time.py   # 응답 시간 테스트
├── Dockerfile                       # 🆕 Docker 이미지 정의
├── docker-compose.yml               # 🆕 Docker Compose 설정
├── .dockerignore                    # 🆕 Docker 무시 파일
└── README-DOCKER.md                 # 🆕 Docker 사용 가이드

**Structure Decision**: 기존 src/ 구조 유지하며 캐시 모듈과 Docker 지원 추가
```

## Complexity Tracking

**헌법 위반 없음 - 추가 정보 불필요**

---

## Phase 0: Outline & Research

**목표**: 성능 최적화 및 Docker 배포의 구체적 접근 방법 연구

### 연구 작업

1. **캐싱 전략 연구** ([research.md](research.md)에 작성)
   - LRU 캐시 vs Redis 비교
   - 캐시 무효화 정책
   - 메모리 사용량 추정
   
2. **동시성 처리 연구**
   - Gradio의 비동기 처리 능력 분석
   - Python asyncio 최적화
   - 스레드 풀 설정
   
3. **Docker 배포 연구**
   - 최소 이미지 크기 (Alpine vs Slim)
   - 멀티 스테이지 빌드
   - 보안 베스트 프랙티스
   
4. **성능 테스트 도구 선정**
   - locust (부하 테스트)
   - pytest-benchmark (성능 벤치마크)
   - docker stats (리소스 모니터링)

**출력**: research.md (모든 미결정 사항 해결)

---

## Phase 1: Design & Contracts

**전제조건**: research.md 완료

### 1.1 데이터 모델 설계 (data-model.md)

```python
# 캐시 모델
@dataclass
class CacheEntry:
    key: str                    # 임베딩 해시
    embedding: List[float]      # 임베딩 벡터
    created_at: datetime
    access_count: int = 0
    last_accessed: datetime = None

# 캐시 통계
@dataclass
class CacheStats:
    total_requests: int
    cache_hits: int
    cache_misses: int
    avg_response_time_ms: float
```

### 1.2 캐시 서비스 인터페이스 (contracts/cache_contract.py)

```python
class ICacheService(Protocol):
    """캐시 서비스 계약"""
    
    def get(self, key: str) -> Optional[List[float]]:
        """캐시에서 임베딩 조회"""
        ...
    
    def set(self, key: str, embedding: List[float]) -> None:
        """캐시에 임베딩 저장"""
        ...
    
    def get_stats(self) -> CacheStats:
        """캐시 통계 반환"""
        ...
```

### 1.3 Docker 팩토리 정의 (contracts/docker_contract.py)

- Dockerfile 구조 정의
- docker-compose.yml 스키마
- 환경 변수 매핑

### 1.4 빠른 시작 가이드 (quickstart.md)

- Docker 설치 및 실행
- 성능 테스트 실행 방법
- 캐시 통계 확인

---

## Phase 2: Implementation (작업 목록는 tasks.md에서 관리)

**기대 작업 수**: ~15-20개

### 2.1 캐시 구현
- [ ] `src/utils/cache.py` - LRU 캐시 구현
- [ ] `src/services/cache_service.py` - 캐시 서비스 래퍼
- [ ] EmbeddingService 통합 (캐시 추가)

### 2.2 비동기 개선
- [ ] `src/main.py` - Gradio 비동기 최적화
- [ ] 스레드 풀 설정
- [ ] 요청 타임아웃 설정

### 2.3 Docker 배포
- [ ] `Dockerfile` 작성
- [ ] `docker-compose.yml` 작성
- [ ] `.dockerignore` 생성
- [ ] 환경 변수 검증

### 2.4 테스트
- [ ] 캐시 유닛 테스트 (8-10개)
- [ ] 캐시 통합 테스트 (5-7개)
- [ ] 부하 테스트 (3-5개)
- [ ] Docker 컨테이너 테스트

### 2.5 마이그레이션
- [ ] 기존 테스트 실행 (회귀 테스트)
- [ ] 문서 업데이트
- [ ] 배포 가이드 작성

---

## 예상 일정

| Phase | 작업 | 예상 시간 |
|-------|------|---------|
| 0 | 연구 | 1-2시간 |
| 1 | 설계 | 1-2시간 |
| 2 | 구현 | 4-6시간 |
| **총합** | **Phase 7 완료** | **6-10시간** |

---

## 성공 기준

✅ **완료 조건**:
1. 모든 기존 테스트 통과 (회귀 없음)
2. 새로운 테스트 작성 (캐시, 부하)
3. Docker 이미지 생성 및 실행 가능
4. 동시 10+ 사용자 처리 검증
5. 응답 시간 <100ms 달성

✅ **배포 준비**:
- [x] 스펙 명확화 (성능, Docker)
- [ ] 연구 단계 완료 (Phase 0)
- [ ] 구현 단계 완료 (Phase 2)
- [ ] 배포 문서 작성| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
