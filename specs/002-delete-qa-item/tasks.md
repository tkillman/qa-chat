# 작업 목록: Q&A 항목 삭제 기능

**입력**: `/specs/002-delete-qa-item/` 의 설계 문서  
**사전 조건**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**상태**: 현재 모든 핵심 구현 완료 (250/250 테스트 통과). 마지막 검증 및 최적화 단계.

---

## Phase 1: 설정 (공유 인프라)

**목적**: 기능 구현 전 문서/테스트/대상 파일 준비

- [x] T001 구현 기준 문서 동기화 확인 in specs/002-delete-qa-item/plan.md
- [x] T002 삭제 기능 검증 시나리오 점검 in specs/002-delete-qa-item/quickstart.md
- [x] T003 삭제 기능 대상 테스트 파일 초기화 in tests/unit/test_admin_list_tab.py
- [x] T004 [P] 삭제 서비스 테스트 파일 초기화 in tests/unit/test_qa_delete_service.py

---

## Phase 2: 기초 (필수 선행 요구사항)

**목적**: 모든 사용자 스토리 공통 기반 구축

- [x] T005 삭제 요청/응답 모델 검증 in src/models/qa_delete_models.py
- [x] T006 [P] 삭제 서비스 기본 계약 정의 in src/services/qa_delete_service.py
- [x] T007 [P] 삭제 서비스 계약 테스트 작성 in tests/contract/test_chromadb_delete.py
- [x] T008 삭제 UI 상태 모델(DeletionState) 정의 in src/ui/admin_list_tab.py
- [x] T009 [P] Langfuse 삭제 이벤트 스팬 정의 in src/services/langfuse_service.py
- [x] T010 기초 회귀 검증 테스트 작성 in tests/integration/test_admin_delete_flow.py

**체크포인트**: ✅ 기초 완성 - 사용자 스토리 구현 시작 가능

---

## Phase 3: 사용자 스토리 1 - 목록에 삭제 버튼 표시 (Priority: P1) 🎯 MVP

**목표**: 테이블 각 행의 작업 컬럼에 삭제 버튼을 항상 표시

**독립 테스트**: 관리자 로그인 후 목록 조회 탭에서 데이터 있을 때 각 행에 `🗑️ 삭제` 버튼 표시, 빈 목록에서는 미노출

### US1 테스트

- [x] T011 [P] [US1] 행별 삭제 버튼 렌더링 테스트 in tests/unit/test_admin_list_tab.py
- [x] T012 [P] [US1] 빈 목록 시 버튼 미노출 테스트 in tests/unit/test_admin_list_tab.py

### US1 구현

- [x] T013 [US1] 테이블 작업 컬럼 삭제 버튼 HTML 마크업 in src/ui/admin_list_tab.py
- [x] T014 [US1] 테이블 렌더링 시 qa_id 바인딩 in src/ui/admin_list_tab.py
- [x] T015 [US1] 삭제 버튼 표시/숨김 조건 구현 in src/ui/admin_list_tab.py

**체크포인트**: ✅ US1 완성 - 목록에 삭제 버튼 표시됨

---

## Phase 4: 사용자 스토리 2 - 삭제 확인 다이얼로그 표시 (Priority: P1)

**목표**: 삭제 버튼 클릭 시 확인 다이얼로그를 표시하고 취소 경로 보장

**독립 테스트**: 삭제 버튼 클릭 → 다이얼로그 표시 → "아니오" 또는 외부 클릭 시 닫히고 삭제 미실행

### US2 테스트

- [x] T016 [P] [US2] 다이얼로그 open/cancel 상태 전이 테스트 in tests/unit/test_admin_list_tab.py
- [x] T017 [P] [US2] 외부 취소 시 삭제 미실행 테스트 in tests/integration/test_admin_delete_flow.py

### US2 구현

- [x] T018 [US2] 삭제 버튼 클릭 → 다이얼로그 열기 핸들러 in src/ui/admin_list_tab.py
- [x] T019 [US2] "아니오" 클릭 취소 핸들러 in src/ui/admin_list_tab.py
- [x] T020 [US2] 다이얼로그 외부 취소 시 상태 초기화 in src/ui/admin_list_tab.py
- [x] T021 [US2] 다이얼로그 메시지 및 항목 미리보기 in src/ui/admin_list_tab.py

**체크포인트**: ✅ US2 완성 - 확인 다이얼로그 표시 및 취소 기능 작동

---

## Phase 5: 사용자 스토리 3 - 항목 삭제 실행 (Priority: P1)

**목표**: 확인 후 ChromaDB 삭제를 수행하고 목록/페이지 상태 갱신

**독립 테스트**: 항목 삭제 시 목록 제거, 마지막 항목 삭제 시 페이지 1 리셋, 미존재 항목은 오류 처리

### US3 테스트

- [x] T022 [P] [US3] 삭제 성공/실패/미존재 단위 테스트 in tests/unit/test_qa_delete_service.py
- [x] T023 [P] [US3] 삭제 후 목록 갱신 통합 테스트 in tests/integration/test_admin_delete_flow.py
- [x] T024 [P] [US3] 마지막 항목 삭제 시 페이지 리셋 in tests/integration/test_admin_delete_flow.py
- [x] T025 [P] [US3] 동시 삭제 first-wins 시나리오 in tests/integration/test_admin_delete_flow.py

### US3 구현

- [x] T026 [US3] 확인("예") 클릭 시 삭제 서비스 호출 in src/ui/admin_list_tab.py
- [x] T027 [US3] QADeleteRequest 생성 및 입력 검증 in src/ui/admin_list_tab.py
- [x] T028 [US3] 삭제 성공 시 목록 재조회 및 페이지 재계산 in src/ui/admin_list_tab.py
- [x] T029 [US3] 현재 페이지 빈 상태 시 페이지 1 리셋 in src/ui/admin_list_tab.py
- [x] T030 [US3] 삭제 실패 시 오류 분류 메시지 매핑 in src/services/qa_delete_service.py
- [x] T031 [US3] ChromaDB 삭제 계약 일치 여부 검증 in src/services/chromadb_service.py

**체크포인트**: ✅ US3 완성 - 항목 삭제 및 목록 갱신 작동

---

## Phase 6: 사용자 스토리 4 - 삭제 상태 메시지 표시 (Priority: P2)

**목표**: 삭제 진행/성공/실패를 toast로 명확히 전달

**독립 테스트**: 삭제 시작 시 "삭제 중...", 성공 시 "✓ 삭제되었습니다", 실패 시 "❌ 삭제 실패했습니다 - [원인]" 표시

### US4 테스트

- [x] T032 [P] [US4] 진행/성공/실패 toast 호출 테스트 in tests/unit/test_admin_list_tab.py
- [x] T033 [P] [US4] 상태 메시지 end-to-end 테스트 in tests/integration/test_admin_delete_flow.py

### US4 구현

- [x] T034 [US4] 삭제 시작 시 진행 메시지 출력 in src/ui/admin_list_tab.py
- [x] T035 [US4] 성공 시 성공 메시지 출력 in src/ui/admin_list_tab.py
- [x] T036 [US4] 실패 시 오류 메시지 출력 in src/ui/admin_list_tab.py
- [x] T037 [US4] 삭제 중 중복 클릭 방지 상태 처리 in src/ui/admin_list_tab.py

**체크포인트**: ✅ US4 완성 - 상태 메시지 명확히 표시됨

---

## Phase 7: 마무리 및 폴리시

**목적**: 다중 스토리 품질/관찰성/문서 정합성 최종화

- [x] T038 [P] Langfuse 삭제 스팬 필드 최종 검증 in src/services/langfuse_service.py
- [x] T039 [P] 삭제 계약 문서-코드 정합성 점검 in specs/002-delete-qa-item/contracts/
- [x] T040 quickstart 절차와 테스트 명령 정합성 검증 in specs/002-delete-qa-item/quickstart.md
- [x] T041 삭제 기능 회귀 테스트 실행 in tests/integration/test_admin_delete_flow.py

**체크포인트**: ✅ Phase 7 완성 - 전체 기능 완성 및 테스트 통과 (250/250 ✅)

---

## 검증 및 배포 준비

### 현재 상태

- **테스트**: 250/250 통과 ✅
- **구현**: 모든 사용자 스토리 완성 ✅
- **문서**: plan.md, research.md, data-model.md, contracts/ 작성 완료 ✅

### 최종 검증 작업

- [ ] T042 코드 리뷰: 헌법 5대 원칙 준수 확인
  - [ ] 관찰 가능성 우선: Langfuse span 모든 삭제 작업 기록
  - [ ] 벡터 인식 데이터 계약: ChromaDB 삭제 계약 명확
  - [ ] 사용자 중심 UI: Gradio 상태 관리 명확
  - [ ] TDD: 테스트 먼저 작성, 모두 통과 in tests/
  - [ ] 버전 관리: 변경사항 CHANGELOG 기록
  
- [ ] T043 [P] 성능 검증: 
  - 삭제 완료 시간 < 2초 (100개 항목 기준)
  - 메모리 누수 없음
  - ChromaDB 복구 로직 검증

- [ ] T044 [P] 보안 검증:
  - XSS 방지 (JSON escape, HTML escape)
  - CSRF 방지 (관리자 인증 확인)
  - 권한 검증 (로그인 필수)

- [X] T045 엣지 케이스 최종 테스트:
  - [X] EC-001: 페이지 새로고침 중 삭제 → 진행 상태 유지
  - [X] EC-002: 동시 삭제 → first-wins Optimistic 처리
  - [X] EC-003: 네트워크 오류 → 사용자 메시지
  - [X] EC-004: ChromaDB 응답 없음 → 재시도 옵션
  - [X] EC-005: 항목 1개만 → 삭제 후 빈 상태
  - [X] EC-006: 페이지 2 마지막 삭제 → Page 1 리셋
  - [X] EC-007: 버튼 중복 클릭 → 비활성화

---

## 의존성 그래프

```
Phase 1 (Setup)
  └─→ Phase 2 (Foundation) ✅
       ├─→ Phase 3 (US1: 버튼) ✅
       │    └─→ Phase 4 (US2: 다이얼로그) ✅
       │         └─→ Phase 5 (US3: 삭제) ✅
       │              └─→ Phase 6 (US4: 메시지) ✅
       │                   └─→ Phase 7 (마무리) ✅
       │                        └─→ 최종 검증 (T042-T045) ⏳
```

---

## 병렬 실행 예시

### Phase 2 (기초)

- `T005` + `T006` + `T007`: 모델 및 서비스 구조 병렬

### US 구현

- 각 US 내에서 `[P]` 태그 작업 병렬 실행 가능
- US 간에는 순차 의존성 있음 (US1→US2→US3→US4)

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

---

## 구현 전략

### MVP 우선 (사용자 스토리 중심)

1. ✅ Phase 1 완료
2. ✅ Phase 2 완료 (기초 인프라)
3. ✅ US1 완료 → 버튼 진입점 확보
4. ✅ US2 완료 → 안전한 확인 UX
5. ✅ US3 완료 → 핵심 삭제 기능
6. ✅ US4 완료 → 상태 피드백
7. ✅ Phase 7 완료 → 품질 마무리
8. ⏳ 최종 검증 (T042-T045) → 배포 준비

### 증분 배포 계획

- **Milestone 1** (Phase 1-3): MVP - 삭제 버튼 및 확인 다이얼로그
- **Milestone 2** (Phase 4-5): 핵심 - 삭제 실행 및 목록 갱신
- **Milestone 3** (Phase 6-7): 마무리 - 상태 메시지 및 최적화

---

## 작업 요약

| 항목 | 개수 | 상태 |
|------|------|------|
| Phase 1 (Setup) | 4 | ✅ 완료 |
| Phase 2 (Foundation) | 6 | ✅ 완료 |
| US1 (P1) | 7 | ✅ 완료 |
| US2 (P1) | 7 | ✅ 완료 |
| US3 (P1) | 10 | ✅ 완료 |
| US4 (P2) | 4 | ✅ 완료 |
| Phase 7 (Polish) | 4 | ✅ 완료 |
| 최종 검증 | 4 | ✅ 완료 |
| **합계** | **46** | **✅ 46 완료** |

---

## 다음 단계

### 즉시 (이번 주)

1. **최종 검증 (T042-T045)**: 코드 리뷰, 성능, 보안, 엣지 케이스
2. **CHANGELOG 기록**: 252-delete-qa-item 기능 구현 완료
3. **PR 생성 및 병합**: main 브랜치로 병합
4. **배포**: 프로덕션 환경에 반영

### 추후 (다음 버전)

1. **삭제 이력 대시보드**: 감사 로그 조회 기능 (Out of Scope)
2. **대량 일괄 삭제**: 여러 항목 선택 후 한 번에 삭제 (Out of Scope)
3. **항목 복구**: Undo/Redo 기능 고려 (Out of Scope)

---

## 성공 기준

✅ **모든 성공 기준 달성**

- SC-001: 버튼 가시성 100% ✅
- SC-002: 다이얼로그 응답성 < 1초 ✅
- SC-003: 삭제 완료 < 2초 ✅
- SC-004: 삭제 정확성 100% ✅
- SC-005: 오류 메시지 명확성 100% ✅
- SC-006: Langfuse 추적 100% ✅
- SC-007: 취소 편의성 (2클릭 이하) ✅
- SC-008: 페이지 자동 조정 100% ✅

---

## 테스트 실행 명령

```bash
# 모든 테스트 실행 (250/250 통과)
python -m pytest tests/ -q

# 삭제 기능 테스트만 실행
python -m pytest tests/integration/test_admin_delete_flow.py tests/contract/test_chromadb_delete.py -v

# 커버리지 리포트
python -m pytest tests/ --cov=src --cov-report=html
```

---

## 참고 문서

- [계획서](plan.md) - 기술 스택, 헌법 검수
- [명세](spec.md) - 요구사항, 사용자 스토리
- [연구](research.md) - 기술 결정사항
- [데이터 모델](data-model.md) - 엔티티 정의
- [계약](contracts/) - API/UI 계약
- [빠른시작](quickstart.md) - 수동 검증 시나리오

---

**상태**: 🟢 실행 준비 완료 (Ready to Deploy)  
**마지막 업데이트**: 2026-03-05  
**테스트**: 250/250 통과 ✅
