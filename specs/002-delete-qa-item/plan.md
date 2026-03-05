# 구현 계획: Q&A 항목 삭제 기능

**브랜치**: `002-delete-qa-item` | **날짜**: 2026-03-05 | **스펙**: [spec.md](spec.md)  
**입력**: 기능 사양 from `/specs/002-delete-qa-item/spec.md`

## 요약

관리자 목록 조회 탭에서 각 Q&A 항목의 삭제 버튼을 통해 ChromaDB에서 항목을 안전하게 삭제할 수 있는 기능입니다. 삭제 시 확인 다이얼로그를 표시하여 실수를 방지하며, 모든 작업이 Langfuse로 계측됩니다.

## 기술 컨텍스트

**언어/버전**: Python 3.11+  
**주요 의존성**: Gradio, ChromaDB, Langfuse, pytest  
**저장소**: ChromaDB (벡터 데이터베이스)  
**테스팅**: pytest (단위 + 통합 테스트)  
**대상 플랫폼**: 웹 (Gradio 사용자 인터페이스)  
**프로젝트 타입**: 웹 애플리케이션 (Gradio UI)  
**성능 목표**: 
- 다이얼로그 표시 응답성: < 1초 (SC-002)
- 삭제 완료 시간: < 2초 (SC-003, 중소 규모 ~100개 항목)

**제약조건**: 
- 페이지당 최대 10개 항목 표시
- 중소 규모 데이터셋 기준 (~100개 항목)
- 네트워크 오류 처리 필수

**규모/범위**: 
- 3개 사용자 스토리 (P1), 1개 추가 요구사항 (P2)
- 4개 엣지 케이스 처리
- 10개 기능 요구사항 + 8개 성공 기준

## 헌법 검증

**GATE: Phase 0 리서치 전에 통과 필수. Phase 1 설계 후 재검증.**

### I. 관찰 가능성 우선 ✓
- **요구사항**: 모든 삭제 작업이 Langfuse를 통해 구조화된 로깅으로 계측되어야 함
- **구현 계획**: 
  - `QADeleteService`에서 Langfuse span으로 삭제 이벤트 기록
  - 요청 (qa_id, admin_user) → 처리 → 결과 (success/failure, message) 추적
  - 오류 발생 시 스택 트레이스 포함
- **상태**: ✓ 준수 (FR-010 포함, app.py의 langfuse_service 사용)

### II. 벡터 인식 데이터 계약 ✓
- **요구사항**: ChromaDB 삭제 작업은 명시적 계약 필요
- **계약 정의**:
  - 입력: QA 항목 ID (hash 기반, QAItem.get_hash_key())
  - 동작: ChromaDB 컬렉션에서 ID 기반으로 문서 삭제
  - 출력: 삭제 성공 여부 + 메시지
  - 폴백: 항목 없음 시 "항목을 찾을 수 없습니다" 오류
- **상태**: ✓ 준수 (QADeleteRequest/QADeleteResult 모델 포함)

### III. 사용자 중심 UI ✓
- **요구사항**: 명확한 입력 검증, 일관된 상태 관리, 실시간 피드백
- **구현 계획**:
  - ✓ 삭제 버튼 명확히 표시 (🗑️ 아이콘 + "삭제" 텍스트)
  - ✓ 확인 다이얼로그 ("이 항목을 삭제하시겠습니까?")
  - ✓ 상태 메시지 (Gradio gr.Info/gr.Error로 toast 알림)
  - ✓ 로딩 중 버튼 비활성화 (상태 관리)
- **상태**: ✓ 준수 (render_qa_cards() + admin_list_tab.py 구현)

### IV. 테스트 주도 개발 (비협상적) ⚠
- **요구사항**: 테스트는 구현 전 작성, TDD 강제
- **계획**:
  - Phase 1에서 test 계약 정의
  - 단위 테스트: QADeleteService (ChromaDB 모의)
  - 통합 테스트: 실제 ChromaDB 삭제 검증
  - UI 테스트: Gradio 버튼/다이얼로그 동작 (필요시 playwright)
- **현재 상태**: ⚠ 테스트 구현 필요 (Phase 2에서 수행)

### V. 버전 관리 및 주요 변경사항 ✓
- **요구사항**: API 계약이 의미적 버전 관리(MAJOR.MINOR.PATCH) 따름
- **적용**:
  - MAJOR 변경 없음 (기존 스키마 유지)
  - MINOR: QADeleteRequest/QADeleteResult 추가
  - PATCH: 버그 수정 (deleteQA 함수 오류 해결)
- **상태**: ✓ 준수 (마이그레이션 필요 없음)

## 프로젝트 구조

### 레이아웃 (이 기능)

```text
specs/002-delete-qa-item/
├── plan.md              # 이 파일 (/speckit.plan 명령어 출력)
├── research.md          # Phase 0 출력 (리서치)
├── data-model.md        # Phase 1 출력 (데이터 모델)
├── quickstart.md        # Phase 1 출력 (시작 가이드)
├── spec.md              # 기능 사양
├── contracts/           # Phase 1 출력 (API 계약)
│   ├── delete-request.md    # 삭제 요청 계약
│   └── delete-response.md   # 삭제 응답 계약
└── tasks.md             # Phase 2 출력 (/speckit.tasks 명령어)
```

### 소스 코드 구조

```text
src/
├── models/
│   ├── qa_delete_models.py  # QADeleteRequest, QADeleteResult
│   └── qa_item.py           # 기존: QA 항목 데이터 모델
├── services/
│   ├── qa_delete_service.py      # 삭제 비즈니스 로직
│   ├── langfuse_service.py       # (기존) 관찰 가능성 계측
│   └── chromadb_service.py       # (기존) ChromaDB 상호작용
└── ui/
    └── admin_list_tab.py         # (수정) 삭제 버튼 + 다이얼로그 UI

tests/
├── unit/
│   └── test_qa_delete_service.py  # 단위 테스트
├── integration/
│   └── test_delete_integration.py  # ChromaDB 통합 테스트
└── contract/
    └── test_delete_contract.py    # 계약 테스트
```

**구조 결정**: 단일 프로젝트 구조 (Option 1) - 기존 src/ 폴더에 삭제 기능 통합

## 복잡성 추적

> 헌법 검증에 위반이 없으므로 이 섹션은 불필요합니다.
> 
> **시작 상태**: ✓ 모든 헌법 원칙 준수
> - 관찰 가능성: Langfuse span으로 계측
> - 벡터 계약: QADeleteRequest/QADeleteResult로 명시
> - 사용자 UI: Gradio 컴포넌트로 구현
> - TDD: Phase 2에서 테스트 구현
> - 버전 관리: 의미적 버전 유지
