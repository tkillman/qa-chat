# Tasks: QA Chat 관리자 및 초기 설정

**Input**: 설계 문서 from `/specs/001-qa-chat-admin-setup/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`

**Tests**: 명세에 독립 테스트 요구가 있으므로 사용자 스토리별 테스트를 포함한다.  
**Organization**: 사용자 스토리(US1~US4) 단위로 독립 구현/검증 가능하도록 구성한다.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: 병렬 가능(다른 파일, 의존성 없음)
- **[Story]**: `US1`, `US2`, `US3`, `US4`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 스펙 확정값과 기본 실행 환경 동기화

- [x] T001 `src/config.py`에 확정 상수 정렬 (`MAX_USER_QUESTION_LENGTH=500`, `MAX_ADMIN_QUESTION_LENGTH=500`, `MAX_ADMIN_ANSWER_LENGTH=2000`, `SIMILARITY_THRESHOLD=0.7`)
- [x] T002 [P] `README.md`와 `QUICKSTART.md`에서 검색 미결과 문구를 `답변을 찾을 수 없습니다`로 통일
- [x] T003 [P] `tests/conftest.py`에서 `.env` 기본값(`ADMIN_PASSWORD=1234`) 테스트 픽스처 정리

---

## Phase 2: Foundational (Blocking)

**Purpose**: 모든 스토리에 공통으로 필요한 인증/저장/관찰성 기반 정리

**⚠️ CRITICAL**: 이 단계 완료 전 사용자 스토리 구현 진행 금지

- [x] T004 `src/main.py`에 전역 인증 상태(`admin_logged_in`) 전이 규칙을 `logged_out ↔ logged_in`으로 명시 정리
- [x] T005 [P] `src/services/langfuse_service.py`에 공통 이벤트 필드(`event_type`, `success`, `error_message`) 확인/보완
- [x] T006 [P] `src/services/file_service.py`에서 JSONL 손상 라인 skip + 경고 로그 계약(`storage-contract.md`) 일치 확인
- [x] T007 `tests/contract/test_chromadb_contract.py`에 임계값 0.7 및 top-1 검색 계약 검증 케이스 추가
- [x] T008 `src/services/embedding_service.py`에서 ChromaDB 기본 임베딩 함수 사용 계약(FR-013) 명시 및 테스트 가능한 훅 정리

**Checkpoint**: Foundation ready

---

## Phase 3: User Story 1 - 초기 로딩 (P1) 🎯 MVP

**Goal**: 앱 시작 시 `init.txt`를 ChromaDB에 로드하고 즉시 검색 가능 상태 제공  
**Independent Test**: 파일 있음/없음/손상 케이스에서 초기화 결과가 명세대로 동작

### Tests (US1)
- [x] T009 [P] [US1] `tests/integration/test_initial_load.py`에 `init.txt` 존재 시 로드 건수 검증
- [x] T010 [P] [US1] `tests/integration/test_initial_load.py`에 `init.txt` 미존재 시 빈 상태 시작 검증
- [x] T011 [US1] `tests/integration/test_initial_load.py`에 손상 라인 skip + 앱 기동 유지 검증

### Implementation (US1)
- [x] T012 [US1] `src/services/init_loader.py`에서 JSONL 유효 레코드만 적재하도록 예외 처리 정교화
- [x] T013 [US1] `src/main.py` `on_startup()`에서 로드 결과(건수/시간/성공여부) 로깅 일관화
- [x] T014 [US1] `src/services/langfuse_service.py`로 startup load 추적 이벤트 연결

**Checkpoint**: US1 단독 동작 가능

---

## Phase 4: User Story 2 - 관리자 로그인/로그아웃 (P1)

**Goal**: 비밀번호 검증 후 관리자 화면 진입, 로그아웃 시 전역 상태 해제  
**Independent Test**: 성공/실패/빈 비밀번호/로그아웃 전이가 독립적으로 검증됨

### Tests (US2)
- [x] T015 [P] [US2] `tests/unit/test_auth.py`에 로그인 실패 후 재시도 허용(잠금 없음) 명시 테스트 추가
- [x] T016 [P] [US2] `tests/integration/test_admin_login.py`에 로그인 성공 시 관리자 컴포넌트 visible 검증
- [x] T017 [US2] `tests/integration/test_admin_login.py`에 로그아웃 버튼 클릭 후 전역 상태 해제 검증 추가

### Implementation (US2)
- [x] T018 [US2] `src/main.py`에 관리자 탭 `로그아웃` 버튼 및 콜백 추가
- [x] T019 [US2] `src/main.py` `admin_login()`/`logout` 콜백을 `contracts/admin-ui-contract.md` 출력 순서와 일치시킴
- [x] T020 [US2] `src/services/auth_service.py`에서 비밀번호 검증 로직을 `.env` 기본값 규칙과 정렬
- [x] T021 [US2] `src/services/langfuse_service.py`에 로그인 성공/실패/로그아웃 이벤트 추적 보강

**Checkpoint**: US2 단독 동작 가능

---

## Phase 5: User Story 3 - 관리자 Q&A 업데이트 (P2)

**Goal**: 관리자 입력으로 ChromaDB + `init.txt` 동시 갱신, 중복 질문 덮어쓰기  
**Independent Test**: 업데이트 후 재시작 시 반영 유지 + 동일 질문 덮어쓰기 확인

### Tests (US3)
- [x] T022 [P] [US3] `tests/unit/test_qa_update.py`에 질문/답변 길이 제한(500/2000) 검증 강화
- [x] T023 [P] [US3] `tests/integration/test_qa_update.py`에 동일 질문 덮어쓰기(정규화 기준) 검증
- [x] T024 [US3] `tests/integration/test_qa_update.py`에 업데이트 후 재시작 재로딩 검증 보강

### Implementation (US3)
- [x] T025 [US3] `src/services/qa_update_service.py`에서 입력 검증 규칙을 `data-model.md`와 일치시킴
- [x] T026 [US3] `src/services/qa_update_service.py`에서 ChromaDB upsert + 파일 반영의 성공/실패 경계 처리 정리
- [x] T027 [US3] `src/services/file_service.py`에 정규화 question 기준 덮어쓰기 저장 보장
- [x] T028 [US3] `src/main.py` `update_qa()` 상태 메시지 및 권한 거부 메시지 계약 정렬
- [x] T029 [US3] `src/services/langfuse_service.py`에 update 성공/실패 이벤트 필드 보강

**Checkpoint**: US3 단독 동작 가능

---

## Phase 6: User Story 4 - 사용자 질문 답변 (P2)

**Goal**: 사용자 질문에 대해 임계값 0.7 기준 top-1 답변 반환, 미검색 문구 고정  
**Independent Test**: 일치/미일치/경계값(0.7) 케이스 독립 검증

### Tests (US4)
- [x] T030 [P] [US4] `tests/unit/test_user_search.py`에 threshold=0.7 경계 테스트 추가
- [x] T031 [P] [US4] `tests/integration/test_user_search_flow.py` 생성: 사용자 탭 검색 end-to-end 테스트
- [x] T032 [US4] `tests/integration/test_user_search_flow.py`에 미검색 문구 exact match 검증

### Implementation (US4)
- [x] T033 [US4] `src/services/user_search_service.py` 반환 정책(top-1, threshold 0.7) 명시화
- [x] T034 [US4] `src/main.py` `search_answer()` 미검색 문구를 exact string으로 고정
- [x] T035 [US4] `src/main.py` 사용자 질문 길이 초과 메시지 및 예외 경로 통일
- [x] T036 [US4] `src/services/langfuse_service.py`에 검색 이벤트(질문, 결과유무, 유사도) 추적 보강

**Checkpoint**: US4 단독 동작 가능

---

## Phase 7: Polish & Cross-Cutting

**Purpose**: 문서/회귀/일관성 마감

- [x] T037 [P] `specs/001-qa-chat-admin-setup/quickstart.md` 시나리오를 실제 구현 단계와 동기화
- [x] T038 [P] `README.md` 운영 메모(전역 로그인 상태 특성, 보안 주의) 추가
- [x] T039 `specs/001-qa-chat-admin-setup/quickstart.md`에 전체 회귀 실행 결과(`pytest -q`) triage 기록
- [x] T040 `specs/001-qa-chat-admin-setup/contracts/admin-ui-contract.md` 및 `specs/001-qa-chat-admin-setup/contracts/storage-contract.md` 구현 일치 체크리스트 작성

---

## Dependencies & Execution Order

### Phase Dependencies
- Phase 1 → Phase 2 → US(3~6) → Phase 7
- US1/US2는 Phase 2 완료 후 병렬 가능
- US3/US4는 Phase 2 완료 후 병렬 가능(단, US3는 관리자 인증 흐름 재사용)

### Story Dependencies
- US1: 독립
- US2: 독립
- US3: US2 인증 상태를 사용하지만 독립 검증 가능
- US4: US1 데이터 로딩 결과를 활용하지만 독립 검증 가능

### Dependency Graph
- Setup → Foundational → {US1, US2} → {US3, US4} → Polish
- 세부 순서: `T001-T003` → `T004-T008` → (`T009-T014` || `T015-T021`) → (`T022-T029` || `T030-T036`) → `T037-T040`

### Parallel Opportunities
- `[P]` 항목은 파일 충돌 없이 병렬 수행 가능
- 테스트 작성(T008~T010, T014~T016, T021~T023, T029~T031)은 각 스토리 내 병렬 가능

---

## Parallel Execution Examples by Story

### US1 병렬 예시
- 병렬 1: `T009` + `T010` (`tests/integration/test_initial_load.py` 내 다른 시나리오 섹션)
- 병렬 2: `T012` (`src/services/init_loader.py`) 와 `T014` (`src/services/langfuse_service.py`)

### US2 병렬 예시
- 병렬 1: `T015` (`tests/unit/test_auth.py`) + `T016` (`tests/integration/test_admin_login.py`)
- 병렬 2: `T020` (`src/services/auth_service.py`) + `T021` (`src/services/langfuse_service.py`)

### US3 병렬 예시
- 병렬 1: `T022` (`tests/unit/test_qa_update.py`) + `T023` (`tests/integration/test_qa_update.py`)
- 병렬 2: `T026` (`src/services/qa_update_service.py`) + `T027` (`src/services/file_service.py`)

### US4 병렬 예시
- 병렬 1: `T030` (`tests/unit/test_user_search.py`) + `T031` (`tests/integration/test_user_search_flow.py`)
- 병렬 2: `T033` (`src/services/user_search_service.py`) + `T036` (`src/services/langfuse_service.py`)

---

## Implementation Strategy

### MVP First
1. Phase 1/2 완료
2. US1 + US2 완료 (초기 로드 + 관리자 인증/로그아웃)
3. 독립 검증 후 데모

### Incremental Delivery
1. US3 추가 (관리자 업데이트)
2. US4 추가 (사용자 검색)
3. Phase 7 정리 및 전체 회귀
