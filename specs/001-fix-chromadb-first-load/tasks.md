# Tasks: 목록 탭 첫 진입 데이터 정합성 수정

**Input**: Design documents from `/specs/001-fix-chromadb-first-load/`  
**Prerequisites**: plan.md (required), spec.md (required)

**Tests**: 사용자 스토리 검증 요구가 명시되어 있으므로 각 스토리별 단위/통합 테스트 작업을 포함한다.

**Organization**: 작업은 사용자 스토리별로 그룹화되어 독립 구현/검증이 가능하다.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 구현 전 공통 준비 및 재현 기준 정리

- [ ] T001 현재 버그 재현 절차와 기대 결과를 specs/001-fix-chromadb-first-load/quickstart.md에 정리
- [ ] T002 [P] 목록 탭 조회 시나리오용 공통 fixture/헬퍼를 tests/conftest.py에 추가

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 사용자 스토리에 공통으로 필요한 로딩 규약을 선행 정리

**⚠️ CRITICAL**: 이 단계 완료 전에는 사용자 스토리 구현을 시작하지 않는다.

- [ ] T003 목록 조회 성공/빈목록/오류 상태 반환 규약을 src/services/qa_list_service.py에 정규화
- [ ] T004 목록 렌더 입력 계약(페이지 정보/총건수/오류 텍스트)을 src/ui/admin_list_tab.py에 통일
- [ ] T005 탭 선택 시 새로고침 트리거 경로를 src/main.py에서 목록 탭 전용으로 명확화

**Checkpoint**: 공통 로딩 경로가 고정되어 사용자 스토리 작업 착수 가능

---

## Phase 3: User Story 1 - 첫 진입 시 정확한 목록 확인 (Priority: P1) 🎯 MVP

**Goal**: 목록 조회 탭 첫 진입 시 정본 저장소 기준 목록만 노출

**Independent Test**: 앱 시작 후 목록 조회 탭 첫 진입 시 화면 목록이 정본 저장소 목록과 완전히 일치하고, 존재하지 않는 항목이 보이지 않아야 함

### Tests for User Story 1

- [ ] T006 [P] [US1] 첫 진입 로드시 비존재 항목 미노출 검증 단위 테스트를 tests/unit/test_admin_list_tab.py에 추가
- [ ] T007 [P] [US1] 첫 탭 진입 시 정본 목록 렌더링 검증 통합 테스트를 tests/integration/test_admin_list.py에 추가

### Implementation for User Story 1

- [ ] T008 [US1] 첫 진입 초기 렌더가 항상 service 조회 응답을 사용하도록 src/ui/admin_list_tab.py 수정
- [ ] T009 [US1] 첫 진입 조회 실패 시 no-retry + 오류/빈목록 상태를 src/services/qa_list_service.py에 구현
- [ ] T010 [US1] 첫 진입 오류/빈목록 표시 메시지를 정책대로 src/ui/admin_list_tab.py에 반영

**Checkpoint**: User Story 1 단독 배포/검증 가능(MVP)

---

## Phase 4: User Story 2 - 새로고침 없는 일관된 재진입 (Priority: P2)

**Goal**: 목록 탭 재진입마다 정본 재조회 기반 최신 목록 유지

**Independent Test**: 목록 탭 진입 → 다른 탭 이동 → 재진입 시 매번 정본 재조회가 일어나고 이전 잘못된 항목이 복원되지 않아야 함

### Tests for User Story 2

- [ ] T011 [P] [US2] 탭 재진입 시 재조회/정합성 유지 통합 테스트를 tests/integration/test_admin_list.py에 추가
- [ ] T012 [P] [US2] 탭 선택 트리거가 매 진입마다 동작하는 단위 테스트를 tests/unit/test_admin_list_tab.py에 추가

### Implementation for User Story 2

- [ ] T013 [US2] 탭 재진입 시마다 목록 재조회 이벤트를 보장하도록 src/ui/admin_list_tab.py 수정
- [ ] T014 [US2] 탭 select 콜백이 매 진입마다 목록 갱신을 유도하도록 src/main.py 수정
- [ ] T015 [US2] 재진입 갱신 시 페이지 상태와 목록 표시 동기화를 src/ui/admin_list_tab.py에서 보정

**Checkpoint**: User Story 2 단독 검증 가능, US1 동작 유지

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: 전 스토리 공통 마무리

- [ ] T016 [P] 목록 탭 관련 회귀 테스트를 실행하고 결과를 specs/001-fix-chromadb-first-load/quickstart.md에 기록
- [ ] T017 [P] 버그 수정 릴리즈 노트를 CHANGELOG.md에 추가
- [ ] T018 성공 기준(SC-001~SC-004) 검증 체크 결과를 specs/001-fix-chromadb-first-load/quickstart.md에 반영

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 즉시 시작 가능
- **Phase 2 (Foundational)**: Phase 1 완료 후 진행, 모든 사용자 스토리를 블로킹
- **Phase 3 (US1)**: Phase 2 완료 후 진행 가능
- **Phase 4 (US2)**: Phase 2 완료 후 진행 가능 (권장 순서: US1 다음)
- **Phase 5 (Polish)**: US1/US2 완료 후 진행

### User Story Dependencies

- **US1 (P1)**: Foundational 완료 후 독립 시작 가능
- **US2 (P2)**: Foundational 완료 후 독립 시작 가능, 단 검증 안정성을 위해 US1 완료 후 착수 권장

### Within Each User Story

- 테스트 작업(T006/T007, T011/T012)을 먼저 작성하고 실패를 확인한 뒤 구현
- 서비스/로딩 정책 구현 후 UI 반영
- 스토리 단위 체크포인트에서 독립 검증 수행

---

## Parallel Opportunities

- **Setup**: T002는 T001과 병렬 수행 가능
- **US1**: T006, T007 병렬 가능
- **US2**: T011, T012 병렬 가능
- **Polish**: T016, T017 병렬 가능

---

## Parallel Example: User Story 1

```bash
Task: "T006 [US1] tests/unit/test_admin_list_tab.py에 첫 진입 단위 테스트 추가"
Task: "T007 [US1] tests/integration/test_admin_list.py에 첫 진입 통합 테스트 추가"
```

## Parallel Example: User Story 2

```bash
Task: "T011 [US2] tests/integration/test_admin_list.py에 재진입 통합 테스트 추가"
Task: "T012 [US2] tests/unit/test_admin_list_tab.py에 재진입 트리거 단위 테스트 추가"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Phase 1 완료
2. Phase 2 완료
3. Phase 3(US1) 완료
4. US1 독립 검증 후 배포 판단

### Incremental Delivery

1. Setup + Foundational으로 로딩 규약 고정
2. US1 적용 후 첫 진입 정합성 확보
3. US2 적용 후 재진입 일관성 확보
4. Polish에서 회귀 및 문서 정리

### Parallel Team Strategy

- 개발자 A: 서비스/정책(`src/services/qa_list_service.py`)
- 개발자 B: UI/탭 이벤트(`src/ui/admin_list_tab.py`, `src/main.py`)
- 개발자 C: 테스트(`tests/unit/test_admin_list_tab.py`, `tests/integration/test_admin_list.py`)
