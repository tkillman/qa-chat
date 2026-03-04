# Tasks: Q&A 항목 삭제 기능

**Input**: Design documents from `/specs/002-delete-qa-item/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: 명세에 독립 테스트 요구가 있으므로 사용자 스토리별 테스트를 포함한다.  
**Organization**: 사용자 스토리(US1~US4) 단위로 독립 구현/검증 가능하도록 구성한다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 가능(다른 파일, 선행 미완료 의존성 없음)
- **[Story]**: `US1`, `US2`, `US3`, `US4`
- 모든 태스크는 정확한 파일 경로를 포함한다

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 기능 구현을 위한 기본 파일/구조/검증 스캐폴드 준비

- [x] T001 삭제 기능 스펙/설계 문서 링크 정합성 점검 in specs/002-delete-qa-item/plan.md
- [x] T002 QA 삭제 모델 파일 구조 점검 및 기본 import 정리 in src/models/qa_delete_models.py
- [x] T003 QA 삭제 서비스 파일 구조 점검 및 기본 import 정리 in src/services/qa_delete_service.py
- [x] T004 [P] 삭제 기능 테스트 파일 골격 정리 in tests/unit/test_qa_delete_service.py
- [x] T005 [P] 삭제 플로우 통합 테스트 골격 정리 in tests/integration/test_admin_delete_flow.py
- [x] T006 [P] ChromaDB 삭제 계약 테스트 골격 정리 in tests/contract/test_chromadb_delete.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 사용자 스토리 공통 선행(데이터 모델/서비스 계약/공통 의존성) 완성

**⚠️ CRITICAL**: 이 단계 완료 전 사용자 스토리 구현 진행 금지

- [x] T007 QADeleteRequest/QADeleteResult 유효성 규칙 확정 in src/models/qa_delete_models.py
- [x] T008 QADeleteService 싱글톤 및 delete_qa_item 서비스 계약 확정 in src/services/qa_delete_service.py
- [x] T009 [P] ChromaDB ID 기반 delete 계약(미존재 시 오류) 확정 in src/services/chromadb_service.py
- [x] T010 [P] Langfuse 삭제 이벤트 표준 필드 계약 확정 in src/services/langfuse_service.py
- [x] T011 [P] QA 목록 재조회/페이지 상태 갱신 계약 확인 in src/services/qa_list_service.py
- [x] T012 공통 실패 메시지 매핑(항목없음/DB오류/네트워크오류) 정의 in src/services/qa_delete_service.py

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - 목록에 삭제 버튼 표시 (Priority: P1) 🎯 MVP

**Goal**: 관리자 목록 조회 카드 헤더 우측에 삭제 버튼을 노출한다.

**Independent Test**: 관리자 로그인 후 목록 조회 진입 시 각 카드에 삭제 버튼이 보이고, 빈 목록에서는 버튼이 표시되지 않는다.

### Tests for User Story 1

- [x] T013 [P] [US1] 카드 렌더링 삭제 버튼 노출 테스트 추가 in tests/unit/test_admin_list_tab.py
- [x] T014 [P] [US1] 빈 목록에서 삭제 버튼 미노출 테스트 추가 in tests/unit/test_admin_list_tab.py
- [x] T015 [US1] 관리자 목록 탭 버튼 노출 통합 시나리오 테스트 추가 in tests/integration/test_admin_delete_flow.py

### Implementation for User Story 1

- [x] T016 [US1] 카드 헤더 우측 삭제 버튼 마크업/스타일 구현 in src/ui/admin_list_tab.py
- [x] T017 [US1] 항목 유무에 따른 삭제 버튼 렌더링 분기 구현 in src/ui/admin_list_tab.py
- [x] T018 [US1] 관리자 탭에서 목록 컴포넌트와 버튼 렌더링 연결 검증 in src/main.py

**Checkpoint**: US1 independently functional

---

## Phase 4: User Story 2 - 삭제 확인 다이얼로그 표시 (Priority: P1)

**Goal**: 삭제 버튼 클릭 시 확인 다이얼로그를 표시하고 취소 경로를 제공한다.

**Independent Test**: 삭제 버튼 클릭 시 다이얼로그가 표시되고, 아니오/외부 클릭 시 닫히며 삭제는 수행되지 않는다.

### Tests for User Story 2

- [x] T019 [P] [US2] 삭제 다이얼로그 상태 전이 단위 테스트 추가 in tests/unit/test_admin_delete_dialog.py
- [x] T020 [P] [US2] 아니오 클릭 취소 동작 단위 테스트 추가 in tests/unit/test_admin_delete_dialog.py
- [ ] T021 [US2] 다이얼로그 표시/닫기 통합 테스트 추가 in tests/integration/test_admin_delete_flow.py

### Implementation for User Story 2

- [x] T022 [US2] DeletionState(show_dialog, selected_qa_id, is_deleting) 정의 in src/ui/admin_list_tab.py
- [x] T023 [US2] 삭제 버튼 클릭 시 다이얼로그 open 핸들러 구현 in src/ui/admin_list_tab.py
- [x] T024 [US2] 예/아니오 버튼 및 외부 클릭 닫기 로직 구현 in src/ui/admin_list_tab.py
- [x] T025 [US2] 삭제 미수행 취소 플로우를 목록 UI 이벤트 체인에 연결 in src/ui/admin_list_tab.py

**Checkpoint**: US2 independently functional

---

## Phase 5: User Story 3 - 항목 삭제 실행 (Priority: P1)

**Goal**: 확인("예") 후 ChromaDB에서 항목 삭제, 목록 갱신, 페이지 리셋 규칙을 적용한다.

**Independent Test**: 특정 항목 삭제 시 목록에서 즉시 제거되고, 페이지 마지막 항목 삭제 시 페이지가 1로 리셋된다.

### Tests for User Story 3

- [x] T026 [P] [US3] QADeleteService 성공/실패/미존재 단위 테스트 보강 in tests/unit/test_qa_delete_service.py
- [x] T027 [P] [US3] ChromaDB delete 계약(존재/미존재) 테스트 보강 in tests/contract/test_chromadb_delete.py
- [x] T028 [US3] 삭제 후 목록 갱신 통합 테스트 추가 in tests/integration/test_admin_delete_flow.py
- [ ] T029 [US3] 페이지 마지막 항목 삭제 시 페이지 리셋 통합 테스트 추가 in tests/integration/test_admin_delete_flow.py

### Implementation for User Story 3

- [x] T030 [US3] delete_qa_item에서 ChromaDB 삭제 및 결과 매핑 구현 in src/services/qa_delete_service.py
- [x] T031 [US3] 삭제 성공 시 QAListService 재조회 및 목록 리렌더링 구현 in src/ui/admin_list_tab.py
- [x] T032 [US3] 마지막 항목 삭제 시 current_page=1 리셋 규칙 구현 in src/ui/admin_list_tab.py
- [x] T033 [US3] 삭제 핸들러를 관리자 목록 탭 이벤트와 연결 in src/main.py

**Checkpoint**: US3 independently functional

---

## Phase 6: User Story 4 - 삭제 상태 메시지 표시 (Priority: P2)

**Goal**: 삭제 진행/성공/실패 상태를 토스트로 사용자에게 명확히 전달한다.

**Independent Test**: 삭제 시작 시 진행 메시지, 성공 시 성공 메시지, 실패 시 원인 포함 오류 메시지가 표시된다.

### Tests for User Story 4

- [x] T034 [P] [US4] 삭제 진행 토스트 호출 단위 테스트 추가 in tests/unit/test_admin_delete_messages.py
- [x] T035 [P] [US4] 삭제 성공/실패 토스트 호출 단위 테스트 추가 in tests/unit/test_admin_delete_messages.py
- [ ] T036 [US4] 상태 메시지 end-to-end 통합 테스트 추가 in tests/integration/test_admin_delete_flow.py

### Implementation for User Story 4

- [x] T037 [US4] 삭제 시작 시 gr.Info("삭제 중...") 처리 구현 in src/ui/admin_list_tab.py
- [x] T038 [US4] 삭제 성공 시 gr.Info("✓ 삭제되었습니다") 처리 구현 in src/ui/admin_list_tab.py
- [x] T039 [US4] 삭제 실패 시 gr.Error("❌ 삭제 실패했습니다 - [원인]") 처리 구현 in src/ui/admin_list_tab.py
- [x] T040 [US4] is_deleting 상태 기반 중복 클릭 방지/버튼 비활성화 구현 in src/ui/admin_list_tab.py

**Checkpoint**: US4 independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 스토리 공통 품질, 성능, 관찰성, 문서 정리

- [x] T041 [P] 삭제 이벤트 observability 필드 최종 정합성 검증 in src/services/langfuse_service.py
- [x] T042 [P] 동시 삭제(Optimistic first-wins) 통합 시나리오 보강 in tests/integration/test_admin_delete_flow.py
- [x] T043 [P] 삭제 성능(<2초) 검증 테스트 추가 in tests/performance/test_response_time.py
- [ ] T044 삭제 기능 quickstart 절차와 실제 동작 일치화 점검 in specs/002-delete-qa-item/quickstart.md
- [x] T045 전체 관련 테스트 스위트 실행 및 결과 기록 in specs/002-delete-qa-item/tasks.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 즉시 시작 가능
- **Phase 2 (Foundational)**: Phase 1 완료 후 시작, 모든 스토리의 선행 차단 단계
- **Phase 3~6 (User Stories)**: Phase 2 완료 후 시작
- **Phase 7 (Polish)**: 모든 대상 스토리 완료 후 시작

### User Story Dependencies

- **US1 (P1)**: Phase 2 이후 즉시 가능, 다른 스토리 의존성 없음
- **US2 (P1)**: Phase 2 이후 즉시 가능, US1 버튼 노출 구현과 동일 파일 협업 주의
- **US3 (P1)**: Phase 2 이후 가능, US2의 확인 플로우와 자연스럽게 결합
- **US4 (P2)**: US3 삭제 실행 경로가 준비된 뒤 적용 권장

### Within Each User Story

- 테스트 태스크를 먼저 작성하고 실패를 확인
- UI 상태 모델/핸들러 구현 후 서비스 연동
- 서비스/계약 정합성 확인 후 통합 테스트 마무리

### Parallel Opportunities

- Phase 1의 `[P]` 태스크(T004~T006) 병렬 가능
- Phase 2의 `[P]` 태스크(T009~T011) 병렬 가능
- Foundation 완료 후 스토리별 테스트 작성 병렬 가능
- US3/US4에서도 단위/계약 테스트 태스크 병렬 가능

---

## Parallel Example: User Story 3

```bash
Task: "T026 [US3] QADeleteService 성공/실패/미존재 단위 테스트 보강 in tests/unit/test_qa_delete_service.py"
Task: "T027 [US3] ChromaDB delete 계약(존재/미존재) 테스트 보강 in tests/contract/test_chromadb_delete.py"
Task: "T028 [US3] 삭제 후 목록 갱신 통합 테스트 추가 in tests/integration/test_admin_delete_flow.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 완료
2. Phase 2 완료 (필수)
3. Phase 3(US1) 완료
4. US1 독립 검증 후 데모

### Incremental Delivery

1. Foundation 완료 후 US1 전달
2. US2(확인 다이얼로그) 추가 전달
3. US3(실제 삭제) 추가 전달
4. US4(상태 메시지) 추가 전달
5. 마지막으로 Phase 7 품질 정리

### Suggested MVP Scope

- **MVP 권장 범위**: US1(버튼 노출) + US2(확인 다이얼로그)까지
- 이유: 사용자 오작동 방지 UI를 포함한 최소 완결 사용자 가치 제공

---

## Validation Checklist

- [x] 모든 태스크가 `- [ ] T### ...` 체크리스트 형식을 준수함
- [x] 사용자 스토리 단계 태스크에 `[US#]` 라벨이 포함됨
- [x] 병렬 가능 태스크에만 `[P]` 라벨을 부여함
- [x] 각 태스크 설명에 정확한 파일 경로를 포함함
- [x] 각 사용자 스토리별 독립 테스트 기준을 명시함
