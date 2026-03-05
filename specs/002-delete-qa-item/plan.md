# 구현 계획: Q&A 항목 삭제 기능

**브랜치**: `002-delete-qa-item` | **날짜**: 2026-03-05 | **명세서**: [spec.md](spec.md)
**입력**: 기능 명세서 `/specs/002-delete-qa-item/spec.md`

## 요약

관리자가 "목록 조회" 탭의 Q&A 테이블에서 각 항목의 삭제 버튼을 클릭하여 항목을 삭제할 수 있는 기능입니다. 삭제 확인 다이얼로그를 통해 실수 삭제를 방지하며, 삭제 후 목록이 자동으로 갱신됩니다. ChromaDB에서 항목을 삭제하고 Langfuse를 통해 모든 작업을 기록합니다.

## 기술 문맥

**언어/버전**: Python 3.12  
**주요 의존성**: Gradio 4.x, ChromaDB, Langfuse, LangChain  
**저장소**: ChromaDB (벡터 저장소) + 파일 기반 초기 데이터 (data/init.txt)  
**테스팅**: pytest 9.x  
**대상 플랫폼**: 웹 애플리케이션 (Gradio)  
**프로젝트 타입**: 웹 서비스 (RAG 기반 Q&A 챗봇)  
**성능 목표**: 삭제 완료 시간 < 2초 (중소 규모 데이터셋 ~100개 항목)  
**제약 사항**: 페이지당 고정 10개 항목 표시, 관리자 인증 필수  
**규모/범위**: 관리자 1명 이상, 사용자 다수

## 헌법 검수 (Constitution Check)

*게이트: Phase 0 연구 전에 통과 필수. Phase 1 설계 후 재검수*

### ✅ 원칙 1: 관찰 가능성 우선
- **요구사항**: 삭제 작업이 Langfuse span으로 기록되어야 함 (FR-010)
- **상태**: 필수 구현 (spec에 요구됨)
- **계획**: `qa_delete_service.py`에 Langfuse span 추가

### ✅ 원칙 2: 벡터 인식 데이터 계약
- **요구사항**: ChromaDB 삭제 계약 명시
- **상태**: 기존 컬렉션 존재, 삭제 후 재건 불필요 (id 기반 삭제)
- **계획**: 삭제 로직에 에러 처리 추가 (EC-002, EC-004)

### ✅ 원칙 3: 사용자 중심 UI
- **요구사항**: Gradio를 통한 명확한 UI, 상태 피드백
- **상태**: 다이얼로그/토스트 알림으로 구현 (FR-005~007)
- **계획**: `admin_list_tab.py`에 UI 상태 관리 구현

### ✅ 원칙 4: 테스트 주도 개발 (비협상적)
- **요구사항**: 구현 전 테스트 작성
- **상태**: 필수 (헌법 정책)
- **계획**: `tests/integration/test_admin_delete_flow.py` 작성

### ✅ 원칙 5: 버전 관리 및 주요 변경사항
- **요구사항**: 스키마 변경 없음 (기존 삭제 API 활용)
- **상태**: 패치 버전 업데이트만 필요
- **계획**: CHANGELOG 기록

**게이트 평가**: ✅ **통과** - 모든 원칙 충족 가능

## 프로젝트 구조

### 문서 (이 기능)

```text
specs/002-delete-qa-item/
├── plan.md              # 이 파일 (/speckit.plan 명령 출력)
├── research.md          # Phase 0 출력 (/speckit.plan 명령)
├── data-model.md        # Phase 1 출력 (/speckit.plan 명령)
├── quickstart.md        # Phase 1 출력 (/speckit.plan 명령)
├── contracts/           # Phase 1 출력 (/speckit.plan 명령)
└── tasks.md             # Phase 2 출력 (/speckit.tasks 명령)
```

### 소스 코드 (저장소 루트)

```text
단일 프로젝트 구조 (선택됨)

src/
├── __init__.py
├── config.py
├── main.py              # Gradio 앱 진입점
├── models/              # 데이터 모델
│   ├── qa_delete_models.py   # QADeleteRequest, QADeleteResult
│   ├── qa_list_models.py     # ListViewState (기존)
│   ├── qa_item.py            # QAItem (기존)
│   └── ...
├── services/            # 비즈니스 로직
│   ├── qa_delete_service.py  # 삭제 로직 (신규)
│   ├── qa_list_service.py    # 목록 조회 (기존)
│   ├── chromadb_service.py   # ChromaDB (기존,수정)
│   ├── langfuse_service.py   # 관찰 가능성 (기존)
│   └── ...
└── ui/                  # 사용자 인터페이스
    ├── admin_list_tab.py     # 관리자 목록 조회 UI (수정)
    └── ...

tests/
├── __init__.py
├── contract/            # 계약 테스트
│   └── test_chromadb_delete.py  # 삭제 계약 테스트 (신규)
├── integration/         # 통합 테스트
│   └── test_admin_delete_flow.py # 삭제 플로우 E2E (신규)
├── unit/                # 단위 테스트
│   └── ...
└── conftest.py          # pytest 고정장치

data/
└── init.txt             # 초기 데이터 (기존)

docker-compose.yml       # ChromaDB 컨테이너
requirements.txt         # Python 의존성
```

**구조 결정**: 단일 프로젝트 구조 선택됨 - 기존 src/models/, src/services/, src/ui/ 레이아웃 활용. 신규: `qa_delete_models.py`, `qa_delete_service.py`, `admin_list_tab.py` 수정, 삭제 관련 테스트 추가

## 복잡성 추적 (Complexity Tracking)

> **헌법 검수 위반이 있는 경우에만 작성**

**평가**: ✅ 위반 사항 없음 - 모든 기능이 기존 아키텍처 내에서 구현 가능합니다.

| 고려 사항 | 정당성 | 선택 이유 |
|-----------|--------|----------|
| ChromaDB 매직 키 기반 삭제 | 가장 빠르고 안정적인 삭제 방식 | UUID 기반 삭제 대비 해시 키 기반이 기존 시스템과 일치 |
| Langfuse span 추가 | 모든 작업 추적 필수 (헌법) | 삭제 이력 감사 추적을 위한 필수 요소 |
| Gradio 다이얼로그 사용 | 사용자 중심 UI 원칙 | 웹 기반 앱에서 확인 없는 삭제는 데이터 손실 위험 증대 |

## 단계별 실행 계획 (Phased Execution)

### Phase 0: 리서치 및 설계 검증
- **산출물**: `research.md` (모든 불명확한 사항 해결)
- **작업사항**:
  - ChromaDB 삭제 계약 재검수
  - Langfuse 추적 포인트 설계
  - Gradio 이벤트 바인딩 검증
  - 오류 처리 전략 (EC-001~007)

### Phase 1: 데이터 모델 + 계약 + 빠른시작
- **산출물**: `data-model.md`, `contracts/`, `quickstart.md`
- **구현 대상**:
  - `models/qa_delete_models.py` (QADeleteRequest, QADeleteResult)
  - `services/qa_delete_service.py` (삭제 로직 + Langfuse)
  - `ui/admin_list_tab.py` (UI 상태 관리)
  - 계약 테스트 (`tests/contract/test_chromadb_delete.py`)
  - 통합 테스트 (`tests/integration/test_admin_delete_flow.py`)
  - Agent context 업데이트

### Phase 2: 작업 분해 (TaskScaffolding)
- **산출물**: `tasks.md` (`/speckit.tasks` 명령으로 생성)
- **목적**: 구현 태스크를 개별 이슈/PR로 분할
