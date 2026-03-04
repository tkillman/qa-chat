# Implementation Plan: 관리자 질문답변 목록 조회

**Branch**: `001-admin-qa-list` | **Date**: 2026-03-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-admin-qa-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

관리자가 로그인 후 ChromaDB에 등록된 모든 질문과 답변 항목을 카드 형식으로 페이징하여 조회할 수 있는 기능입니다. 최신 등록순으로 정렬되며, 페이지당 10/20/50개 선택 가능합니다. Gradio 기반 UI에 통합되며, 기존 관리자 인증 시스템을 활용합니다.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Gradio 4.26+, ChromaDB 0.5+, Langfuse 2.12+  
**Storage**: ChromaDB (벡터 저장소 + 메타데이터), data/init.txt (영구 저장)  
**Testing**: pytest (단위 + 통합), Gradio 테스트  
**Target Platform**: 웹 애플리케이션 (Gradio 서버)  
**Project Type**: Web application (Gradio 기반 단일 서버 애플리케이션)  
**Performance Goals**: 
- 목록 로딩 3초 이내 (SC-001)
- 1000개 항목 환경에서 페이지 로딩 2초 이내 (SC-002)
- 페이지 전환 1초 이내 (SC-003)
**Constraints**: 
- 기존 관리자 인증 시스템과 통합 (FR-001)
- Gradio 컴포넌트만 사용 (헌법 III)
- Langfuse 추적 필수 (헌법 I)
**Scale/Scope**: 
- 예상 최대 항목 수: 10,000개
- 동시 관리자 접속: 1-5명
- 읽기 전용 기능 (수정/삭제 없음)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. 관찰 가능성 우선 ✅
- **평가**: PASS
- **근거**: ChromaDB 조회 작업에 Langfuse 추적 추가 필요. 목록 로딩, 페이지 전환, 새로고침 작업을 모두 추적합니다.
- **구현**: 
  - `list_qa_items()` 함수에 Langfuse span 추가
  - 페이지 로딩 시간 지표 기록
  - 오류 발생 시 스택 트레이스 포함

### II. 벡터 인식 데이터 계약 ✅
- **평가**: PASS
- **근거**: 이 기능은 벡터 검색을 수행하지 않고 ChromaDB에서 메타데이터만 조회합니다. 기존 계약을 유지하며 새로운 계약 불필요.
- **구현**: ChromaDB collection의 `get()` 메서드 사용 (검색 없음)

### III. 사용자 중심 UI ✅
- **평가**: PASS
- **근거**: Gradio 컴포넌트로 구현. 관리자 탭에 새로운 "목록 조회" 서브탭 추가.
- **구현**:
  - 명확한 페이징 컨트롤 (이전/다음 버튼, 페이지 표시)
  - 카드 형식으로 읽기 쉬운 레이아웃
  - 로딩 상태 표시 (진행 표시기)
  - 오류 메시지 명확히 표시

### IV. 테스트 주도 개발 ✅
- **평가**: PASS
- **근거**: 테스트 우선 작성 필수
- **구현**:
  - 단위 테스트: 페이징 로직, 정렬 로직
  - 통합 테스트: ChromaDB에서 실제 데이터 조회
  - UI 테스트: Gradio 컴포넌트 상호작용
  - TDD 사이클: Red (테스트 작성) → Green (구현) → Refactor

### V. 버전 관리 및 주요 변경사항 ✅
- **평가**: PASS
- **근거**: 읽기 전용 기능이므로 기존 데이터나 API에 영향 없음. MINOR 버전 증가 (새로운 UI 컴포넌트 추가).
- **구현**: 마이그레이션 불필요, 기존 데이터 구조 유지

### 전체 평가: ✅ PASS
모든 헌법 원칙을 준수합니다. 복잡성 예외 불필요.

## Project Structure

### Documentation (this feature)

```text
specs/001-admin-qa-list/
├── spec.md             # 기능 명세서 (완료)
├── plan.md             # 이 파일 (진행 중)
├── research.md         # Phase 0 출력 (생성 예정)
├── data-model.md       # Phase 1 출력 (생성 예정)
├── quickstart.md       # Phase 1 출력 (생성 예정)
├── contracts/          # Phase 1 출력 (생성 예정 - 이 기능은 읽기 전용으로 새 계약 없음)
├── checklists/         # 품질 체크리스트
│   └── requirements.md # 요구사항 체크리스트 (완료)
└── tasks.md            # Phase 2 출력 (speckit.tasks 명령으로 생성)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── qa_item.py           # 기존 QA 항목 모델
│   └── qa_list_models.py    # 신규: 목록 조회용 모델 (PaginationState, QAListItem)
├── services/
│   ├── auth_service.py      # 기존 인증 서비스
│   ├── chromadb_service.py  # 기존 ChromaDB 서비스 (list 메서드 추가)
│   ├── langfuse_service.py  # 기존 Langfuse 서비스
│   └── qa_list_service.py   # 신규: 목록 조회 서비스
├── ui/
│   └── admin_list_tab.py    # 신규: 관리자 목록 조회 UI 컴포넌트
├── config.py                # 기존 설정 (페이징 설정 추가)
└── main.py                  # 기존 메인 앱 (admin_list_tab 통합)

tests/
├── unit/
│   ├── test_qa_list_service.py  # 신규: 목록 서비스 단위 테스트
│   └── test_pagination.py       # 신규: 페이징 로직 단위 테스트
├── integration/
│   └── test_admin_list.py       # 신규: 관리자 목록 통합 테스트
└── contract/
    # 계약 테스트 불필요 (읽기 전용, 기존 ChromaDB 계약 사용)
```

**Structure Decision**: 단일 프로젝트 구조 유지. 기존 `src/` 디렉토리에 새로운 서비스와 모델 추가. UI는 `src/ui/` 디렉토리에 모듈화하여 main.py에서 import. 이는 기존 프로젝트의 관례를 따르며 Gradio 탭 기반 구조와 자연스럽게 통합됩니다.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - 모든 헌법 원칙을 준수하므로 복잡성 예외 불필요.
