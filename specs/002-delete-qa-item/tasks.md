# Tasks: Q&A 항목 삭제 기능

**Input**: Design documents from `/specs/002-delete-qa-item/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 기능 구현 전에 문서/테스트/대상 파일 경로를 실행 가능 상태로 정렬

- [X] T001 구현 기준 문서 동기화 확인 in specs/002-delete-qa-item/plan.md
- [X] T002 삭제 기능 검증 시나리오 점검 및 실행 명령 정리 in specs/002-delete-qa-item/quickstart.md
- [X] T003 삭제 기능 대상 테스트 파일 초기 상태 점검 in tests/unit/test_admin_list_tab.py
- [X] T004 [P] 삭제 서비스 테스트 파일 초기 상태 점검 in tests/unit/test_qa_delete_service.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 사용자 스토리 구현 전에 필요한 공통 토대 완성

**⚠️ CRITICAL**: 이 단계 완료 전에는 어떤 사용자 스토리도 시작하지 않음

- [X] T005 삭제 요청/응답 모델 검증 규칙 정렬 in src/models/qa_delete_models.py
- [X] T006 [P] 삭제 서비스 기본 계약 정렬 in src/services/qa_delete_service.py
- [X] T007 [P] 삭제 서비스 계약 테스트 기준 정렬 in tests/contract/test_chromadb_delete.py
- [X] T008 삭제 UI 상태 모델(DeletionState) 공통 규칙 정렬 in src/ui/admin_list_tab.py
- [X] T009 [P] Langfuse 삭제 이벤트 필드 계약 정렬 in src/services/langfuse_service.py
- [X] T010 Foundational 회귀 검증 테스트 추가/정렬 in tests/integration/test_admin_delete_flow.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 목록에 삭제 버튼 표시 (Priority: P1) 🎯 MVP

**Goal**: 테이블 각 행의 작업 컬럼에 삭제 버튼을 항상 표시

**Independent Test**: 관리자 로그인 후 목록 조회 탭에서 데이터가 있으면 각 행에 `🗑️ 삭제` 버튼이 보이고, 빈 목록에서는 버튼이 노출되지 않음

### Tests for User Story 1

- [X] T011 [P] [US1] 행별 삭제 버튼 렌더링 테스트 구현 in tests/unit/test_admin_list_tab.py
- [X] T012 [P] [US1] 빈 목록 시 삭제 버튼 미노출 테스트 구현 in tests/unit/test_admin_list_tab.py

### Implementation for User Story 1

- [X] T013 [US1] 테이블 작업 컬럼 삭제 버튼 마크업 정리 in src/ui/admin_list_tab.py
- [X] T014 [US1] 테이블 렌더링 시 qa_id 바인딩 정리 in src/ui/admin_list_tab.py
- [X] T015 [US1] 삭제 버튼 표시/숨김 조건 정리 in src/ui/admin_list_tab.py

**Checkpoint**: US1 is independently functional and testable

---

## Phase 4: User Story 2 - 삭제 확인 다이얼로그 표시 (Priority: P1)

**Goal**: 삭제 버튼 클릭 시 확인 다이얼로그를 표시하고 취소 경로를 보장

**Independent Test**: 삭제 버튼 클릭 시 다이얼로그가 열리고, `아니오` 또는 외부 클릭 시 닫히며 삭제는 실행되지 않음

### Tests for User Story 2

- [X] T016 [P] [US2] 다이얼로그 open/cancel 상태 전이 테스트 구현 in tests/unit/test_admin_list_tab.py
- [X] T017 [P] [US2] 외부 취소/아니오 클릭 삭제 미실행 테스트 구현 in tests/integration/test_admin_delete_flow.py

### Implementation for User Story 2

- [X] T018 [US2] 삭제 버튼 클릭 시 다이얼로그 열기 핸들러 정리 in src/ui/admin_list_tab.py
- [X] T019 [US2] `아니오` 클릭 취소 핸들러 정리 in src/ui/admin_list_tab.py
- [X] T020 [US2] 다이얼로그 외부 취소 시 상태 초기화 정리 in src/ui/admin_list_tab.py
- [X] T021 [US2] 다이얼로그 표시 메시지 및 선택 항목 미리보기 정리 in src/ui/admin_list_tab.py

**Checkpoint**: US2 is independently functional and testable

---

## Phase 5: User Story 3 - 항목 삭제 실행 (Priority: P1)

**Goal**: 확인(`예`) 후 ChromaDB 삭제를 수행하고 목록/페이지 상태를 정확히 갱신

**Independent Test**: 특정 항목 삭제 시 목록에서 제거되고, 마지막 항목 삭제 시 페이지 1로 리셋되며, 미존재 항목은 오류로 처리

### Tests for User Story 3

- [X] T022 [P] [US3] 삭제 성공/실패/미존재 단위 테스트 구현 in tests/unit/test_qa_delete_service.py
- [X] T023 [P] [US3] 삭제 후 목록 갱신 통합 테스트 구현 in tests/integration/test_admin_delete_flow.py
- [X] T024 [P] [US3] 마지막 항목 삭제 시 페이지 리셋 통합 테스트 구현 in tests/integration/test_admin_delete_flow.py
- [X] T025 [P] [US3] 동시 삭제 first-wins 시나리오 테스트 구현 in tests/integration/test_admin_delete_flow.py

### Implementation for User Story 3

- [X] T026 [US3] 확인(`예`) 클릭 시 삭제 서비스 호출 체인 정리 in src/ui/admin_list_tab.py
- [X] T027 [US3] `QADeleteRequest` 생성 및 입력 검증 연계 정리 in src/ui/admin_list_tab.py
- [X] T028 [US3] 삭제 성공 시 목록 재조회 및 현재 페이지 재계산 정리 in src/ui/admin_list_tab.py
- [X] T029 [US3] 현재 페이지 빈 상태 시 페이지 1 리셋 로직 정리 in src/ui/admin_list_tab.py
- [X] T030 [US3] 삭제 실패 시 오류 분류 메시지 매핑 정리 in src/services/qa_delete_service.py
- [X] T031 [US3] ChromaDB 삭제 계약 일치 여부 검증 정리 in src/services/chromadb_service.py

**Checkpoint**: US3 is independently functional and testable

---

## Phase 6: User Story 4 - 삭제 상태 메시지 표시 (Priority: P2)

**Goal**: 삭제 진행/성공/실패를 toast로 명확히 전달하고 중복 클릭을 방지

**Independent Test**: 삭제 시작 시 `삭제 중...`, 성공 시 `✓ 삭제되었습니다`, 실패 시 `❌ 삭제 실패했습니다 - [원인]`가 표시됨

### Tests for User Story 4

- [X] T032 [P] [US4] 진행/성공/실패 toast 호출 테스트 구현 in tests/unit/test_admin_list_tab.py
- [X] T033 [P] [US4] 상태 메시지 end-to-end 테스트 구현 in tests/integration/test_admin_delete_flow.py

### Implementation for User Story 4

- [X] T034 [US4] 삭제 시작 시 진행 메시지 출력 정리 in src/ui/admin_list_tab.py
- [X] T035 [US4] 성공 시 성공 메시지 출력 정리 in src/ui/admin_list_tab.py
- [X] T036 [US4] 실패 시 오류 메시지 출력 정리 in src/ui/admin_list_tab.py
- [X] T037 [US4] 삭제 중 중복 클릭 방지 상태 처리 정리 in src/ui/admin_list_tab.py

**Checkpoint**: US4 is independently functional and testable

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 다중 스토리에 걸친 품질/관찰성/문서 정합성 마무리

- [X] T038 [P] 삭제 Langfuse span 필드 최종 검증 및 보정 in src/services/langfuse_service.py
- [X] T039 [P] 삭제 관련 계약 문서-코드 정합성 점검 in specs/002-delete-qa-item/contracts/qa-delete-service-contract.md
- [X] T040 quickstart 절차와 실제 테스트 명령 정합성 검증 in specs/002-delete-qa-item/quickstart.md
- [X] T041 삭제 기능 회귀 테스트 실행 및 결과 기록 in tests/integration/test_admin_delete_flow.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 즉시 시작 가능
- **Phase 2 (Foundational)**: Phase 1 완료 후 시작, 모든 User Story를 블로킹
- **Phase 3~6 (User Stories)**: Phase 2 완료 후 시작
- **Phase 7 (Polish)**: 모든 목표 User Story 완료 후 시작

### User Story Dependencies

- **US1 (P1)**: Foundational 이후 독립 시작 가능
- **US2 (P1)**: US1 버튼 진입점에 의존
- **US3 (P1)**: US2 확인 다이얼로그 플로우에 의존
- **US4 (P2)**: US3 삭제 실행 플로우에 의존

### Within Each User Story

- 테스트 작성/보강 → 구현 → 통합/회귀 검증 순서
- `[P]` 태스크는 동일 단계 내 병렬 실행 가능

---

## Parallel Execution Examples

### User Story 1

- `T011` + `T012`를 병렬 실행하여 US1 렌더링 검증 시간을 단축

### User Story 3

- `T022` + `T023` + `T024`를 병렬 실행 후 `T026`부터 순차 구현

---

## Implementation Strategy

### MVP First (User Story 1 중심)

1. Phase 1 완료
2. Phase 2 완료
3. US1(Phase 3) 완료 후 독립 검증
4. 필요 시 즉시 데모/배포

### Incremental Delivery

1. US1 완료 → 버튼 진입점 확보
2. US2 완료 → 안전한 확인 UX 확보
3. US3 완료 → 핵심 삭제 기능 완성
4. US4 완료 → 상태 피드백 완성
5. Polish 완료 → 문서/추적/회귀 안정화
