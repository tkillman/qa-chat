# 작업 목록: Q&A 항목 삭제 기능

**입력**: `/specs/002-delete-qa-item/` 설계 문서  
**필수 조건**: plan.md ✅, spec.md ✅  
**기반 기능**: Feature 001 QA Chat 관리자 및 초기 설정  
**예상 시간**: ~3.5시간

---

## 작업 형식

```
- [ ] [TaskID] [P?] [Story?] 설명 (파일 경로)
```

- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story?**: User Story 레이블 (US1, US2, US3, US4)
- 경로: `src/`, `tests/` (repo root)

---

## Phase 1: 설정 (공유 인프라)

**목적**: 프로젝트 초기화 및 기본 구조

- [ ] T001 데이터 모델 파일 생성: `src/models/qa_delete_models.py`
- [ ] T002 서비스 파일 생성: `src/services/qa_delete_service.py`
- [ ] T003 테스트 파일 생성: `tests/unit/test_qa_delete_service.py`
- [ ] T004 [P] 통합 테스트 파일 생성: `tests/integration/test_admin_delete_flow.py`
- [ ] T005 [P] 계약 테스트 생성: `tests/contract/test_chromadb_delete.py`

---

## Phase 2: 기초 (차단 선행 작업)

**목적**: 모든 User Story 구현 전 필수 완료 항목

⚠️ **임계점**: 이 Phase 완료 전 User Story 작업 불가

- [ ] T006 QADeleteRequest, QADeleteResult dataclass 정의 (FR-003, FR-010 요구사항)
  - 파일: `src/models/qa_delete_models.py`
  - `qa_id: str` (Hash ID)
  - `admin_user: str` (관리자 이름)
  - `timestamp: datetime` (요청 시간)
  - `success: bool`, `message: str`, `error_reason: Optional[str]`

- [ ] T007 QADeleteService 클래스 뼈대 생성
  - 파일: `src/services/qa_delete_service.py`
  - 싱글톤 패턴 (Feature 001처럼)
  - `delete_qa_item(qa_id: str) -> QADeleteResult` 메서드 시그니처

- [ ] T008 [P] ChromaDBService 의존성 확인
  - 파일: `src/services/chromadb_service.py` (기존)
  - `delete()` 메서드 동작 검증 (EC-002 동시성 테스트)
  - 실패 시 Exception 발생 확인

- [ ] T009 [P] QAListService 의존성 확인
  - 파일: `src/services/qa_list_service.py` (기존)
  - `list_items()` 메서드 재호출 가능 확인 (FR-004 목록 갱신)

- [ ] T010 LangfuseService 통합 계획
  - 파일: `src/services/langfuse_service.py` (기존)
  - 삭제 이벤트 span 기록 패턴 검토 (FR-010)
  - `start_span()`, `end_span()` 사용 방식 정의

**임계점**: 기초 작업 완료 ✅ → User Story 병렬 구현 시작

---

## Phase 3: User Story 1 - 목록에 삭제 버튼 표시 (P1) 🎯 MVP

**목표**: 관리자 목록 조회에서 각 Q&A 항목의 title/header 우측에 삭제 버튼(🗑️) 표시

**독립 테스트**: 관리자 로그인 → "목록 조회" 진입 → 각 항목에 🗑️ 버튼 확인

### T011~T015: 삭제 버튼 UI 구현

- [ ] T011 admin_list_tab.py에서 카드 렌더링 로직 분석
  - 파일: `src/ui/admin_list_tab.py`
  - `render_qa_cards()` 함수 구조 파악
  - Gradio Button 위치 결정 (title row 우측)

- [ ] T012 [P] [US1] 삭제 버튼 컴포넌트 추가
  - 파일: `src/ui/admin_list_tab.py`
  - 각 카드에 `gr.Button("🗑️", size="sm")` 추가
  - Acceptance: US1 acceptance scenario 1 통과 (버튼 표시)

- [ ] T013 [P] [US1] 빈 목록일 때 버튼 미표시 로직
  - 파일: `src/ui/admin_list_tab.py`
  - `if items_list:` 조건으로 보호
  - Acceptance: US1 acceptance scenario 2 통과 (버튼 미표시)

- [ ] T014 [US1] 단위 테스트: 버튼 표시 검증
  - 파일: `tests/unit/test_admin_list_ui.py` (신규)
  - Mock QAListService로 데이터 1개 이상 반환 시 버튼 표시 확인

- [ ] T015 [US1] 수동 테스트: 목록 조회 탭 시각적 확인
  - `python src/main.py` 실행
  - 관리자 로그인 (1234) → 목록 조회 확인
  - 각 항목의 title 우측에 🗑️ 버튼 확인

---

## Phase 4: User Story 2 - 삭제 확인 다이얼로그 표시 (P1)

**목표**: 삭제 버튼 클릭 시 "이 항목을 삭제하시겠습니까?" 확인 모달 표시

**독립 테스트**: 삭제 버튼 클릭 → 다이얼로그 표시 → "아니오" 클릭 시 닫힘

### T016~T021: 확인 다이얼로그 구현

- [ ] T016 [P] 삭제 상태 State 정의
  - 파일: `src/ui/admin_list_tab.py`
  - `deletion_state = gr.State({"show_dialog": False, "selected_qa_id": None})`

- [ ] T017 [US2] 다이얼로그 상태 표시 로직
  - 파일: `src/ui/admin_list_tab.py`
  - `gr.Markdown("이 항목을 삭제하시겠습니까?").visible = deletion_state["show_dialog"]`

- [ ] T018 [US2] 다이얼로그 "예", "아니오" 버튼 추가
  - 파일: `src/ui/admin_list_tab.py`
  - `gr.Button("예")` 및 `gr.Button("아니오")`
  - "아니오"는 `deletion_state["show_dialog"] = False`로 설정

- [ ] T019 [P] [US2] 다이얼로그 외부 클릭 닫기
  - 파일: `src/ui/admin_list_tab.py`
  - Gradio 모달 기능으로 외부 클릭 시 닫기 (gr.ModalInterface 또는 커스텀)

- [ ] T020 [US2] 단위 테스트: 다이얼로그 상태 관리
  - 파일: `tests/unit/test_admin_delete_dialog.py` (신규)
  - Mock 클릭 이벤트 → 상태 변경 확인

- [ ] T021 [US2] 통합 테스트: 다이얼로그 표시/닫기
  - 파일: `tests/integration/test_admin_delete_flow.py`
  - 삭제 버튼 → 다이얼로그 표시 → "아니오" → 닫힘 검증

---

## Phase 5: User Story 3 - 항목 삭제 실행 (P1)

**목표**: 다이얼로그 "예" 클릭 시 ChromaDB에서 항목 삭제 + 목록 갱신

**독립 테스트**: 로그인 → 목록 특정 항목 확인 → 삭제 → 목록 애서 제거 확인

### T022~T030: 삭제 로직 구현

- [ ] T022 [P] QADeleteService.delete_qa_item() 구현
  - 파일: `src/services/qa_delete_service.py`
  - ChromaDB delete() 호출 (QA ID 기반)
  - 실패 시 예외 처리 및 오류 메시지 반환

- [ ] T023 [P] [US3] Langfuse span 기록 로직
  - 파일: `src/services/qa_delete_service.py`
  - `start_span("delete_qa_item", {"qa_id": qa_id, "admin_user": admin_user})`
  - 성공/실패 메타데이터 기록 (FR-010)

- [ ] T024 [US3] 삭제 버튼 클릭 핸들러 구현
  - 파일: `src/ui/admin_list_tab.py`
  - `on_delete_button_click()` 콜백 정의
  - QADeleteService 호출 + 결과 반환

- [ ] T025 [US3] [P] 목록 갱신 로직
  - 파일: `src/ui/admin_list_tab.py`
  - 삭제 성공 후 `QAListService.list_items()` 재호출
  - 목록 UI 상태 업데이트 (FR-004)

- [ ] T026 [US3] [P] 페이지 번호 리셋 로직
  - 파일: `src/ui/admin_list_tab.py`
  - 마지막 페이지의 마지막 항목 삭제 시 `current_page = 1` 설정
  - 첫 페이지 데이터 로드 (FR-008)

- [ ] T027 [US3] 단위 테스트: QADeleteService.delete_qa_item()
  - 파일: `tests/unit/test_qa_delete_service.py`
  - ChromaDB 모의 (Mock)로 삭제 호출 검증
  - EC-002 동시성 테스트 (첫 번째 성공, 두 번째 "항목 없음" 오류)

- [ ] T028 [US3] 계약 테스트: ChromaDB delete() 동작
  - 파일: `tests/contract/test_chromadb_delete.py`
  - 실제 ChromaDB에서 delete() 후 get() 실패 확인
  - 삭제 ID 존재 안 함 검증

- [ ] T029 [US3] 통합 테스트: 삭제 후 목록 갱신
  - 파일: `tests/integration/test_admin_delete_flow.py`
  - 삭제 전 항목 1개 확인 → 삭제 → 목록에서 제거 확인

- [ ] T030 [US3] 통합 테스트: 페이지 리셋
  - 파일: `tests/integration/test_admin_delete_flow.py`
  - 페이지 2의 마지막 항목 삭제 시 페이지가 1로 리셋 확인

---

## Phase 6: User Story 4 - 삭제 상태 메시지 표시 (P2)

**목표**: 삭제 중 "삭제 중..." 표시, 완료 후 "✓ 삭제됨" 또는 오류 메시지

**독립 테스트**: 삭제 버튼 → "예" → 상태 메시지 확인

### T031~T036: 상태 메시지 구현

- [ ] T031 [P] 삭제 진행 상태 변수 추가
  - 파일: `src/ui/admin_list_tab.py`
  - `deletion_in_progress = gr.State(False)`
  - 삭제 중 버튼 비활성화

- [ ] T032 [US4] 삭제 중 메시지 표시
  - 파일: `src/ui/admin_list_tab.py`
  - 삭제 시작 시 `gr.Info("삭제 중...")` (FR-005)

- [ ] T033 [US4] 삭제 성공 메시지
  - 파일: `src/ui/admin_list_tab.py`
  - 임무 성공 시 `gr.Info("✓ 삭제되었습니다")` (FR-006)
  - 3초 후 자동 소멸

- [ ] T034 [US4] 삭제 실패 메시지
  - 파일: `src/ui/admin_list_tab.py`
  - 예외 발생 시 `gr.Error("❌ 삭제 실패했습니다 - [원인]")` (FR-007)
  - 원인: "항목을 찾을 수 없습니다", "네트워크 오류", "ChartomaDDB 오류" 등

- [ ] T035 [US4] 단위 테스트: 메시지 콜백
  - 파일: `tests/unit/test_admin_delete_messages.py` (신규)
  - gr.Info/Error 호출 검증

- [ ] T036 [US4] 통합 테스트: 메시지 흐름
  - 파일: `tests/integration/test_admin_delete_flow.py`
  - 삭제 진행 중 → 성공 메시지 → 자동 소멸 검증

---

## Phase 7: Edge Cases & Error Handling

**목적**: 모든 엣지 케이스 및 오류 상황 처리

### T037~T048: Edge Case 테스트 및 처리

- [ ] T037 [P] Edge Case EC-001: 삭제 중 페이지 새로고침
  - 파일: `tests/integration/test_admin_delete_edge_cases.py` (신규)
  - 상태 유지 검증

- [ ] T038 [P] Edge Case EC-002: 동시 삭제 요청
  - 파일: `tests/integration/test_admin_delete_edge_cases.py`
  - Optimistic 패턴 검증 (첫 성공, 두 번째 오류)

- [ ] T039 [P] Edge Case EC-003: 네트워크 오류
  - 파일: `tests/integration/test_admin_delete_edge_cases.py`
  - 재시도 옵션 제공 확인

- [ ] T040 [P] Edge Case EC-004: ChromaDB 응답 불가
  - 파일: `tests/integration/test_admin_delete_edge_cases.py`
  - 타임아웃 처리 및 오류 메시지

- [ ] T041 [P] Edge Case EC-005: 목록 항목 1개만 있을 때 삭제
  - 파일: `tests/integration/test_admin_delete_edge_cases.py`
  - 빈 상태 메시지 표시 확인 (SC-005)

- [ ] T042 [P] Edge Case EC-006: 페이지 2의 마지막 항목 삭제
  - 파일: `tests/integration/test_admin_delete_edge_cases.py`
  - 페이지 1로 리셋 확인 (FR-008)

- [ ] T043 [P] Edge Case EC-007: 삭제 버튼 빠른 다중 클릭
  - 파일: `tests/integration/test_admin_delete_edge_cases.py`
  - 중복 삭제 방지 (버튼 비활성화)

- [ ] T044 [P] 성능 테스트: 삭제 완료 < 2초
  - 파일: `tests/performance/test_delete_performance.py` (신규)
  - 100개 항목 데이터셋에서 측정 (SC-003)

- [ ] T045 [P] 성능 테스트: 응답성 < 1초
  - 파일: `tests/performance/test_delete_performance.py`
  - 다이얼로그 표시 시간 측정 (SC-002)

- [ ] T046 [P] 감사 추적 테스트: Langfuse span 기록
  - 파일: `tests/integration/test_langfuse_delete_trace.py` (신규)
  - 모든 삭제 작업이 기록되는지 검증 (SC-006, FR-010)

- [ ] T047 [P] 권한 검증 테스트: 관리자만 접근
  - 파일: `tests/integration/test_admin_delete_auth.py` (신규)
  - 비관리자는 목록 탭 자체 접근 불가 (기존 Feature 001 검증)

- [ ] T048 권한 검증 테스트: 인증된 관리자 확인
  - 파일: `tests/integration/test_admin_delete_auth.py`
  - 로그인 상태 + 관리자 역 확인 (Assumption 검증)

---

## Phase 8: 통합 및 마무리

**목적**: 전체 흐름 검증 및 배포 준비

### T049~T055: 최종 통합 테스트

- [ ] T049 [P] 모든 단위 테스트 통과
  - 명령어: `pytest tests/unit/ -v`
  - 예상: 100% 통과

- [ ] T050 [P] 모든 계약 테스트 통과
  - 명령어: `pytest tests/contract/ -v`
  - 예상: ChromaDB 삭제 계약 검증

- [ ] T051 모든 통합 테스트 통과
  - 명령어: `pytest tests/integration/ -v`
  - 예상: 전체 삭제 흐름 검증

- [ ] T052 [P] 모든 성능 테스트 통과
  - 명령어: `pytest tests/performance/ -v`
  - 예상: 응답 < 1초, 삭제 < 2초

- [ ] T053 전체 테스트 스위트 실행
  - 명령어: `pytest tests/ -v --cov`
  - 예상: qa_delete_service.py 70% 이상 커버리지

- [ ] T054 수동 E2E 테스트: 전체 삭제 흐름
  - `python src/main.py` 실행
  - 로그인 → 목록 조회 → 항목 선택 → 삭제 → 확인 → 완료 → 목록 갱신 확인

- [ ] T055 [P] 코드 리뷰 및 문서화
  - 파일: 모든 신규/수정 파일
  - Docstring 추가, 주석 정리, README 업데이트

---

## Phase 9: 배포 및 검증

### T056~T062: 배포 체크리스트

- [ ] T056 git 커밋
  - 메시지: "feat(002): Q&A 항목 삭제 기능 구현"

- [ ] T057 [P] 브랜치 머지 준비
  - `002-delete-qa-item` → `main`

- [ ] T058 최종 테스트 실행
  - 명령어: `pytest tests/ -v --cov=src`
  - 결과 기록

- [ ] T059 성능 검증 최종
  - 100개 항목 데이터셋에서 평균 성능 측정
  - 목표: 삭제 < 2초, 응답 < 1초 달성 확인 (SC-003, SC-002)

- [ ] T060 Langfuse 대시보드 확인
  - 삭제 이벤트 span 기록 확인 (FR-010, SC-006)
  - 성공/실패 비율, 평균 응답 시간

- [ ] T061 스크린샷 및 문서 업데이트
  - CHANGELOG.md에 기능 추가
  - README.md에 사용 방법 기술

- [ ] T062 배포 완료
  - 브랜치 머지: `002-delete-qa-item` → `main`
  - 태그: `v0.2.0` (Feature 002 완료)

---

## 의존성 그래프

```
관리자 인증 (Feature 001)
    ↓
T001-T005 (파일 생성)
    ↓
T006-T010 (기초 설정) ← BLOCKER
    ↓
┌───────────────────────────────┬─────────────────────────┬──────────────────┐
│ US1: 버튼 표시                │ US2: 다이얼로그        │ US3: 삭제 실행   │
│ T011-T015 (병렬)              │ T016-T021 (병렬)       │ T022-T030        │
│ (의존: T006-T010)            │ (의존: T006-T010)     │ (의존: T006-T010)│
└───────────────────────────────┴─────────────────────────┴──────────────────┘
    ↓                                  ↓                         ↓
 US1 완료                           US2 완료                  US3 완료
    ↓                                  ↓                         ↓
 MVP 슬라이스 1을 단독으로 배포  가능

┌────────────────────────────────┐
│ US4: 상태 메시지 표시         │
│ T031-T036                      │
│ (의존: T022-T025 완료)       │
└────────────────────────────────┘
    ↓
 US4 완료
    ↓
 전체 기능 완료

T037-T048: Edge Cases & Error Handling (모든 US 후)
T049-T062: 통합, 배포
```

---

## 병렬 실행 계획

**동시 실행 가능 작업 그룹** (US1-US3은 독립적):

```
그룹 1 (시작):
- T001-T005: 파일 생성
- T006-T010: 기초 작업

그룹 2 (병렬, T006-T010 완료 후):
- 개발자 A: US1 UI (T011-T015)
- 개발자 B: US2 다이얼로그 (T016-T021)
- 개발자 C: US3 삭제 로직 (T022-T030)

그룹 3:
- US4 메시지 (T031-T036) [US3 완료 후]

그룹 4:
- 테스트 (T037-T048) [모든 US 완료 후]

그룹 5:
- 배포 (T056-T062) [모든 테스트 완료 후]
```

**단일 개발자**: 순차 실행 (총 ~3.5시간)

---

## 테스트 요약

| 테스트 종류 | 파일 | 케이스 수 | 예상 결과 |
|-----------|------|---------|--------|
| 단위 테스트 | `tests/unit/` | ~12 | ✅ PASS |
| 계약 테스트 | `tests/contract/` | ~3 | ✅ PASS |
| 통합 테스트 | `tests/integration/` | ~15 | ✅ PASS |
| 성능 테스트 | `tests/performance/` | ~3 | ✅ < 2초 |
| Edge Case | `tests/integration/` | ~7 | ✅ PASS |
| **총합** | | **~40** | **100% ✅** |

---

## 성공 기준

모든 작업 완료 시:

- ✅ 모든 62개 기존 테스트 통과 (Feature 001)
- ✅ 모든 40개 신규 테스트 통과 (Feature 002)
- ✅ 코드 커버리지: qa_delete_service.py 70% 이상
- ✅ 성능: 삭제 < 2초, 응답 < 1초
- ✅ Langfuse: 모든 삭제 span 기록됨
- ✅ 수동 E2E: 전체 삭제 흐름 작동
- ✅ 배포 체크리스트: 전 항목 완료

---

**예상 완료일**: 2026-03-05 + 3.5시간  
**상태**: 준비 완료 ✅ → 구현 시작 🚀

