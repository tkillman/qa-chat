# Tasks: 관리자 질문답변 목록 조회

**Feature**: 001-admin-qa-list  
**Input**: Design documents from `/specs/001-admin-qa-list/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: TDD 방식으로 진행 - 테스트를 먼저 작성하고 구현합니다 (헌법 IV)

**Organization**: 작업은 User Story별로 그룹화되어 독립적인 구현 및 테스트를 지원합니다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 속한 User Story (US1, US2, US3, US4)
- 설명에 정확한 파일 경로 포함

## Path Conventions

단일 프로젝트 구조:
- 소스: `src/models/`, `src/services/`, `src/ui/`, `src/main.py`
- 테스트: `tests/unit/`, `tests/integration/`
- 스크립트: `scripts/`

---

## Phase 1: Setup (공유 인프라)

**목적**: 프로젝트 초기화 및 기본 디렉토리 구조 생성

- [X] T001 src/ui/ 디렉토리 생성 (Gradio UI 컴포넌트용)
- [X] T002 tests/unit/ 및 tests/integration/ 디렉토리 확인
- [X] T003 [P] scripts/ 디렉토리 생성 (마이그레이션 스크립트용)

---

## Phase 2: Foundational (차단 선행 작업)

**목적**: 모든 User Story가 의존하는 핵심 인프라

**⚠️ 중요**: 이 단계가 완료되어야 User Story 작업 시작 가능

### 데이터 모델 (TDD: 테스트 먼저)

- [X] T004 [P] tests/unit/test_qa_list_models.py 생성 - QAListItem 테스트 작성 (실패 예상)
- [X] T005 [P] tests/unit/test_qa_list_models.py에 PaginationState 테스트 추가 (실패 예상)
- [X] T006 [P] tests/unit/test_qa_list_models.py에 ListViewState 테스트 추가 (실패 예상)

### 모델 구현

- [X] T007 src/models/qa_list_models.py 생성 - QAListItem 클래스 정의
- [X] T008 src/models/qa_list_models.py에 PaginationState 클래스 추가 (불변 패턴 적용)
- [X] T009 src/models/qa_list_models.py에 ListViewState 클래스 추가
- [X] T010 T004-T006 테스트 통과 확인 (Green 단계)

### ChromaDB 확장 (선택적)

- [ ] T011 [P] src/services/chromadb_service.py에 get_all_items() 메서드 추가 (선택 - collection.get()으로 대체 가능)

### 마이그레이션 준비

- [X] T012 [P] scripts/generate_test_data.py 생성 - 30개 테스트 데이터 생성 스크립트
- [X] T013 [P] scripts/migrate_add_created_at.py 생성 - 기존 데이터에 created_at 추가 (선택적)

**Checkpoint**: 모델 및 데이터 준비 완료 - User Story 구현 시작 가능

---

## Phase 3: User Story 1 + 2 - 기본 목록 조회 및 페이지 네비게이션 (Priority: P1) 🎯 MVP

**Goal**: 관리자가 로그인 후 질문답변 목록을 카드 형식으로 페이징하여 조회 (최신 등록순)

**Independent Test**: 관리자 로그인 → 목록 조회 탭 접근 → 카드 형식의 10개 항목 표시 → 이전/다음 버튼으로 페이지 이동

**Note**: US1과 US2는 함께 구현 (페이징 네비게이션 없는 목록은 불완전)

### Tests for US1 & US2 (TDD: Red 단계)

- [X] T014 [P] [US1] tests/unit/test_qa_list_service.py 생성 - list_items() 메서드 테스트 작성 (실패 예상)
- [X] T015 [P] [US1] tests/unit/test_qa_list_service.py에 정렬 로직 테스트 추가 (최신 등록순)
- [X] T016 [P] [US2] tests/unit/test_qa_list_service.py에 페이징 로직 테스트 추가
- [X] T017 [P] [US1] tests/integration/test_admin_list.py 생성 - 전체 목록 조회 통합 테스트 (실패 예상)

### Service Implementation (TDD: Green 단계)

- [X] T018 [US1] src/services/qa_list_service.py 생성 - QAListService 클래스 골격
- [X] T019 [US1] src/services/qa_list_service.py에 list_items(page, items_per_page) 메서드 구현
- [X] T020 [US1] ChromaDB collection.get() 호출 및 QAListItem 변환 로직 추가
- [X] T021 [US1] 최신 등록순(created_at 내림차순) 정렬 로직 추가
- [X] T022 [US2] 페이징 로직 추가 (offset 계산, 슬라이싱)
- [X] T023 [US1] Langfuse 추적 통합 - trace 및 spans (chromadb_get_all, sort_items, paginate) 추가
- [X] T024 [US1] get_qa_list_service() 싱글톤 팩토리 함수 추가
- [X] T025 [US1] T014-T017 테스트 통과 확인 (Green 단계)

### UI Implementation

- [X] T026 [US1] src/ui/admin_list_tab.py 생성 - render_qa_cards() 함수 구현 (HTML/CSS 카드 레이아웃)
- [X] T027 [US1] src/ui/admin_list_tab.py에 render_empty_message() 함수 추가 (빈 목록 처리)
- [X] T028 [US1] src/ui/admin_list_tab.py에 create_admin_list_tab() 함수 추가 - Gradio 컴포넌트 구조
- [X] T029 [US2] create_admin_list_tab()에 페이징 컨트롤 추가 (이전/다음 버튼, 페이지 정보 표시)
- [X] T030 [US2] 이전/다음 버튼 클릭 이벤트 핸들러 구현 (PaginationState 업데이트)
- [X] T031 [US2] 첫 페이지/마지막 페이지에서 버튼 비활성화 로직 추가
- [X] T032 [US1] Gradio State 컴포넌트로 current_page, items_per_page 상태 관리

### Main Integration

- [X] T033 [US1] src/main.py에 admin_list_tab import 추가
- [X] T034 [US1] src/main.py의 관리자 탭에 "목록 조회" 서브탭 통합
- [X] T035 [US1] 관리자 로그인 상태 확인 로직 연결 (로그인 시에만 접근 가능)

### Manual Testing & Refinement

- [X] T036 [US1] 앱 실행 → 관리자 로그인 → 목록 조회 탭 확인 (수동 테스트)
- [X] T037 [US2] 페이지 이동 테스트 (이전/다음 버튼, 페이지 정보 표시 확인)
- [X] T038 [US1] 카드 레이아웃 스타일 조정 (스크롤 박스, 색상, 간격)
- [X] T039 [US1] Langfuse 대시보드에서 추적 확인 (admin_list_qa_items trace)

**Checkpoint**: MVP 완성 - 기본 목록 조회 및 페이징 기능이 독립적으로 작동

---

## Phase 4: User Story 3 - 페이지당 항목 수 변경 (Priority: P2)

**Goal**: 관리자가 10개, 20개, 50개 중 선택하여 페이지당 표시 항목 수 변경 (첫 페이지로 자동 이동)

**Independent Test**: 목록 화면에서 드롭다운으로 20개 선택 → 첫 페이지로 이동 → 20개 항목 표시 확인

### Tests (TDD: Red 단계)

- [ ] T040 [P] [US3] tests/unit/test_qa_list_service.py에 items_per_page 변경 테스트 추가 (실패 예상)
- [ ] T041 [P] [US3] tests/integration/test_admin_list.py에 항목 수 변경 통합 테스트 추가
  
### Implementation (TDD: Green 단계)

- [ ] T042 [US3] src/ui/admin_list_tab.py에 items_per_page Dropdown 컴포넌트 추가 (choices=[10, 20, 50], value=10)
- [ ] T043 [US3] Dropdown 변경 이벤트 핸들러 구현 - PaginationState.change_items_per_page() 호출
- [ ] T044 [US3] 항목 수 변경 시 current_page=1로 리셋 로직 추가
- [ ] T045 [US3] T040-T041 테스트 통과 확인

### Manual Testing

- [ ] T046 [US3] 드롭다운으로 10→20→50 변경 테스트 (수동)
- [ ] T047 [US3] 2페이지에서 항목 수 변경 시 1페이지로 이동 확인

**Checkpoint**: 페이지당 항목 수 선택 기능 독립적으로 작동

---

## Phase 5: User Story 4 - 총 항목 수 표시 (Priority: P3)

**Goal**: "총 N개의 항목" 정보를 페이지 네비게이션 영역에 표시

**Independent Test**: 목록 화면에서 "총 37개의 항목" 메시지 확인

### Tests (TDD: Red 단계)

- [ ] T048 [P] [US4] tests/unit/test_qa_list_service.py에 total_items 반환 테스트 추가 (실패 예상)

### Implementation (TDD: Green 단계)

- [ ] T049 [US4] src/ui/admin_list_tab.py에 total_items Markdown 컴포넌트 추가
- [ ] T050 [US4] PaginationState.get_total_items_text() 메서드 호출하여 텍스트 생성
- [ ] T051 [US4] 빈 목록일 때 "총 0개의 항목" 또는 "등록된 항목이 없습니다" 표시
- [ ] T052 [US4] T048 테스트 통과 확인

### Manual Testing

- [ ] T053 [US4] 다양한 항목 수(0, 5, 37, 100개)에서 총 항목 수 표시 확인 (수동)

**Checkpoint**: 총 항목 수 표시 기능 완성

---

## Phase 6: Additional Features (수동 새로고침 & 빈 목록 처리)

**Goal**: 수동 새로고침 버튼 및 빈 목록 상태 처리

### 수동 새로고침 (Clarification 결정 사항)

- [ ] T054 [P] src/ui/admin_list_tab.py에 새로고침 버튼 추가 (🔄 icon)
- [ ] T055 새로고침 버튼 클릭 시 현재 페이지 유지하며 ChromaDB에서 재조회
- [ ] T056 새로고침 시 Langfuse 추적 기록 (refresh 메타데이터)

### 빈 목록 처리 (FR-011)

- [ ] T057 [P] src/ui/admin_list_tab.py에서 items가 비어있을 때 페이징 요소 모두 숨김 (visible=False)
- [ ] T058 빈 목록 메시지 "등록된 질문답변이 없습니다" 표시
- [ ] T059 tests/integration/test_admin_list.py에 빈 목록 테스트 추가

### 오류 처리 (FR-012)

- [ ] T060 [P] src/services/qa_list_service.py에 try-except 블록으로 ChromaDB 오류 처리
- [ ] T061 오류 발생 시 ListViewState.error() 반환 및 Langfuse에 ERROR 레벨 기록
- [ ] T062 src/ui/admin_list_tab.py에서 error_message 표시 로직 추가

**Checkpoint**: 추가 기능 완성 (새로고침, 빈 목록, 오류 처리)

---

## Phase 7: Polish & Cross-Cutting Concerns

**목적**: 여러 User Story에 영향을 미치는 개선 사항

### 코드 품질

- [ ] T063 [P] 모든 파일에 docstring 추가 (Google 스타일)
- [ ] T064 [P] 타입 힌팅 완성도 확인 (mypy 실행 - 선택적)
- [ ] T065 코드 리뷰 및 리팩토링 (중복 제거, 명명 개선)

### 성능 최적화

- [ ] T066 [P] 1000개 항목 환경에서 페이지 로딩 시간 측정 (SC-002: 2초 이내)
- [ ] T067 필요 시 캐싱 로직 추가 (선택적)

### 테스트 커버리지

- [ ] T068 [P] pytest --cov 실행하여 커버리지 확인 (목표: 80% 이상)
- [ ] T069 [P] 누락된 엣지 케이스 테스트 추가

### 문서화

- [ ] T070 [P] README.md에 "목록 조회" 기능 섹션 추가
- [ ] T071 [P] CHANGELOG.md에 새 기능 기록
- [ ] T072 quickstart.md 검증 (7단계 가이드 실행 가능 확인)

### 최종 검증

- [ ] T073 전체 테스트 스위트 실행 (pytest tests/ -v)
- [ ] T074 Spec의 모든 Acceptance Scenarios 수동 테스트
- [ ] T075 헌법 준수 재확인 (Langfuse 추적, Gradio 사용, 테스트 존재, 버전 관리)

**Checkpoint**: 기능 완전성 및 품질 달성 ✅

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← 모든 User Story가 의존
    ↓
    ├─→ Phase 3: US1 + US2 (P1) 🎯 MVP
    ├─→ Phase 4: US3 (P2)
    ├─→ Phase 5: US4 (P3)
    └─→ Phase 6: Additional Features
         ↓
Phase 7 (Polish)
```

### User Story Dependencies

- **US1 + US2 (P1)**: Foundational 완료 후 시작 가능, 다른 Story 의존성 없음
- **US3 (P2)**: US1+US2 완료 권장하지만 독립적으로 구현 가능
- **US4 (P3)**: US1+US2 완료 권장하지만 독립적으로 구현 가능
- **Additional Features**: US1+US2 완료 필수

### Within Each User Story

1. **Tests 먼저** (Red) - 테스트 작성 및 실패 확인
2. **Implementation** (Green) - 테스트를 통과시키는 최소 구현
3. **Refinement** (Refactor) - 코드 개선 및 리팩토링
4. **Manual Testing** - UI 수동 테스트 및 검증

### Parallel Opportunities

#### Foundational Phase (Phase 2)
- T004, T005, T006 (테스트 작성) 병렬 가능
- T011, T012, T013 (ChromaDB 확장, 스크립트) 병렬 가능

#### US1 + US2 Phase (Phase 3)
- T014, T015, T016, T017 (테스트 작성) 병렬 가능
- Service 구현 완료 후:
  - T026, T027 (UI 함수들) 병렬 가능

#### US3 Phase (Phase 4)
- T040, T041 (테스트 작성) 병렬 가능

#### US4 Phase (Phase 5)
- T048 (테스트) 독립적

#### Additional Features (Phase 6)
- T054, T057, T060 (각 기능의 첫 작업) 병렬 가능

#### Polish Phase (Phase 7)
- T063, T064, T068, T069, T070, T071 모두 병렬 가능

---

## Parallel Example: Foundational Phase

```bash
# 동시에 3개 작업 시작
Terminal 1: pytest tests/unit/test_qa_list_models.py -k QAListItem  # T004
Terminal 2: pytest tests/unit/test_qa_list_models.py -k PaginationState  # T005
Terminal 3: python scripts/generate_test_data.py  # T012

# 모델 구현 후
Terminal 1: pytest tests/unit/test_qa_list_models.py  # T010 검증
```

## Parallel Example: US1 + US2 Implementation

```bash
# Service 구현 완료 후 UI 함수 병렬 작성
Terminal 1: code src/ui/admin_list_tab.py  # T026: render_qa_cards()
Terminal 2: code src/ui/admin_list_tab.py  # T027: render_empty_message()

# 통합 후 수동 테스트
Terminal 1: python src/main.py  # T036-T039
```

---

## Implementation Strategy

### MVP Scope (최소 기능 제품)

**Phase 1-3만 구현**하면 MVP 완성:
- Setup
- Foundational (모델 + 서비스)
- US1 + US2 (기본 목록 조회 + 페이징)

이것만으로도 관리자가:
- 질문답변 목록을 카드 형식으로 조회 가능
- 페이지 이동으로 전체 데이터 탐색 가능
- 최신 등록순으로 정렬된 목록 확인 가능

### Incremental Delivery

1. **Week 1**: Phase 1-3 (MVP) ← 즉시 가치 제공
2. **Week 2**: Phase 4 (US3) ← 사용성 개선
3. **Week 3**: Phase 5-6 (US4 + Additional) ← 완성도 증가
4. **Week 4**: Phase 7 (Polish) ← 품질 향상

각 단계마다 독립적으로 테스트 및 배포 가능.

---

## Testing Strategy

### TDD Workflow (헌법 IV 준수)

모든 작업은 Red-Green-Refactor 사이클을 따릅니다:

1. **Red**: 실패하는 테스트 작성
   - 예: T014 - list_items() 테스트 → 실패 (함수 미존재)
   
2. **Green**: 테스트를 통과시키는 최소 구현
   - 예: T018-T025 - list_items() 구현 → 테스트 통과
   
3. **Refactor**: 코드 개선 (테스트 통과 유지)
   - 예: T063-T065 - 리팩토링 및 최적화

### Test Levels

- **Unit Tests**: 모델, 서비스 로직 (tests/unit/)
- **Integration Tests**: ChromaDB 연동, 전체 흐름 (tests/integration/)
- **Manual UI Tests**: Gradio 화면 동작 확인

---

## Success Criteria Checklist

구현 완료 시 다음을 모두 만족해야 함:

- [ ] **SC-001**: 로그인 후 3초 이내 목록 첫 페이지 표시
- [ ] **SC-002**: 1000개 항목에서 페이지 로딩 2초 이내
- [ ] **SC-003**: 페이지 전환 1초 이내
- [ ] **SC-004**: 항목 수 변경 후 1초 이내 목록 표시
- [ ] **SC-005**: 모든 텍스트가 화면에 맞게 표시 (스크롤 지원)
- [ ] **SC-006**: 페이지 정보 (번호, 전체 페이지, 총 항목) 즉시 파악 가능

### Functional Requirements Checklist

- [ ] **FR-001**: 관리자 인증 확인 (로그인 필수)
- [ ] **FR-002**: ChromaDB 전체 항목 조회
- [ ] **FR-003**: 기본 페이지당 10개
- [ ] **FR-004**: 10/20/50개 선택 가능
- [ ] **FR-005**: 이전/다음 버튼 제공
- [ ] **FR-006**: 첫/마지막 페이지에서 버튼 비활성화
- [ ] **FR-007**: "페이지 X/Y" 표시
- [ ] **FR-008**: "총 N개" 표시
- [ ] **FR-009**: 카드 형식 + 질문/답변 포함
- [ ] **FR-010**: 항목 수 변경 시 첫 페이지 이동
- [ ] **FR-011**: 빈 목록 시 메시지 + 페이징 숨김
- [ ] **FR-012**: 오류 시 친화적 메시지
- [ ] **FR-013**: 긴 텍스트 스크롤 박스
- [ ] **FR-014**: 최신 등록순 정렬
- [ ] **FR-015**: 수동 새로고침 버튼

---

## Total Task Count

- **Setup**: 3 tasks
- **Foundational**: 10 tasks
- **US1 + US2 (P1)**: 26 tasks 🎯
- **US3 (P2)**: 8 tasks
- **US4 (P3)**: 6 tasks
- **Additional Features**: 9 tasks
- **Polish**: 13 tasks

**Total**: 75 tasks

**Critical Path**: Setup → Foundational → US1+US2 (39 tasks for MVP)

**Parallel Potential**: ~15 tasks can run in parallel (marked with [P])

---

**준비 완료! 구현을 시작하세요 🚀**

quickstart.md를 참고하여 단계별로 진행하거나, 이 tasks.md를 체크리스트로 사용하세요.
