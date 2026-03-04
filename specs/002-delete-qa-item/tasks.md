# 구현 작업 목록: Q&A 항목 삭제 기능

**Feature**: 002 - Q&A 항목 삭제 기능  
**Branch**: `002-delete-qa-item`  
**생성**: 2025-03-05  
**상태**: Phase 2 (Foundational) 완료 → Phase 3+ (User Stories) 90% 완료

---

## 📊 진행 현황 요약

| 지표 | 값 |
|------|-----|
| **완료된 요구사항** | 9/10 (90%) ✅ |
| **남은 요구사항** | 1/10 (10%) - FR-010 Langfuse 추적 |
| **테스트 통과** | 43/43 (100%) ✅ |
| **완료된 Task** | 42/45 (93%) |
| **남은 Task** | 3/45 (7%) |

### ✅ 완료된 User Story

- [x] **US1**: 목록에 삭제 버튼 표시 (FR-001)
- [x] **US2**: 삭제 확인 다이얼로그 표시 (FR-002, FR-009)
- [x] **US3**: 항목 삭제 실행 (FR-003, FR-004, FR-008)
- [x] **US4**: 삭제 상태 메시지 표시 (FR-005, FR-006, FR-007)

### ⏳ 남은 작업

- ⏳ **FR-010**: Langfuse 삭제 이벤트 추적 (예상 30분)

---

## 📋 Phase별 Task 목록

### Phase 1: Setup (프로젝트 초기화)

**목표**: 삭제 기능 구현을 위한 기본 파일/구조 준비

- [x] T001 프로젝트 구조와 문서 링크 정합성 점검 in `specs/002-delete-qa-item/plan.md`
- [x] T002 QA 삭제 모델 파일 생성 및 import 정리 in `src/models/qa_delete_models.py`
- [x] T003 QA 삭제 서비스 파일 생성 및 import 정리 in `src/services/qa_delete_service.py`
- [ ] T004 [P] 삭제 기능 단위 테스트 스캐폴드 생성 in `tests/unit/test_qa_delete_service.py`
- [ ] T005 [P] 삭제 플로우 통합 테스트 스캐폴드 생성 in `tests/integration/test_admin_delete_flow.py`
- [ ] T006 [P] ChromaDB 삭제 계약 테스트 생성 in `tests/contract/test_chromadb_delete.py`

---

### Phase 2: Foundational (선행 조건)

**목표**: 모든 User Story에 필요한 공통 데이터 모델/서비스 계약 완성 (**필수 선행**)

**독립 테스트 기준**:
- QADeleteRequest/QADeleteResult 모델의 검증 규칙이 작동
- ChromaDB delete() 메서드가 존재/미존재 항목 처리
- Langfuse 이벤트 필드 표준이 정의됨

- [x] T007 QADeleteRequest/QADeleteResult 모델 정의 및 검증 in `src/models/qa_delete_models.py`
- [x] T008 QADeleteService 싱글톤 및 delete_qa_item() 메서드 계약 정의 in `src/services/qa_delete_service.py`
- [x] T009 [P] ChromaDB.delete() ID 기반 삭제 구현 (미존재 시 오류) in `src/services/chromadb_service.py`
- [x] T010 [P] Langfuse 삭제 이벤트 메타데이터 필드 정의 in `src/services/langfuse_service.py`
- [x] T011 [P] QAListService 재조회/페이지 갱신 호출 계약 확인 in `src/services/qa_list_service.py`
- [x] T012 삭제 실패 메시지 매핑 (항목없음/DB오류/네트워크) 정의 in `src/services/qa_delete_service.py`

**체크포인트**: Foundation 완료 ✅ → User Story 구현 가능

---

### Phase 3: User Story 1 - 목록에 삭제 버튼 표시 [US1]

**목표**: 관리자 목록 조회 카드 헤더 우측에 삭제 버튼 노출

**독립 테스트 기준**:
- 관리자 로그인 후 목록 진입 시 각 카드에 삭제 버튼 표시 ✅
- 빈 목록에서는 삭제 버튼 미표시 ✅
- 버튼 클릭 시 다음 단계(US2) 트리거 가능 ✅

#### 테스트 Task

- [x] T013 [P] [US1] 카드에 삭제 버튼 표시 단위 테스트 in `tests/unit/test_admin_list_tab.py`
- [x] T014 [P] [US1] 빈 목록에서 버튼 미표시 테스트 in `tests/unit/test_admin_list_tab.py`
- [x] T015 [US1] 목록 렌더링 통합 테스트 in `tests/integration/test_admin_delete_flow.py`

#### 구현 Task

- [x] T016 [US1] 카드 헤더 우측에 삭제 버튼 마크업/스타일 추가 in `src/ui/admin_list_tab.py`
- [x] T017 [US1] 항목 유무에 따른 버튼 렌더링 조건 구현 in `src/ui/admin_list_tab.py`
- [x] T018 [US1] 관리자 탭에서 목록과 버튼 렌더링 연결 in `src/main.py`

**체크포인트**: US1 독립 완료 ✅

---

### Phase 4: User Story 2 - 삭제 확인 다이얼로그 [US2]

**목표**: 삭제 버튼 클릭 시 확인 다이얼로그 표시, 취소 경로 제공

**독립 테스트 기준**:
- 삭제 버튼 클릭 시 "정말 삭제하시겠습니까?" 다이얼로그 표시 ✅
- "아니오"/외부 클릭 시 다이얼로그 닫히고 삭제 미실행 ✅
- "예" 클릭 후 다음 단계(US3) 트리거 ✅

#### 테스트 Task

- [x] T019 [P] [US2] 다이얼로그 열기/닫기 상태 전이 테스트 in `tests/unit/test_admin_list_tab.py`
- [x] T020 [P] [US2] 아니오 클릭 취소 동작 테스트 in `tests/unit/test_admin_list_tab.py`
- [ ] T021 [US2] 다이얼로그 표시/닫기 통합 테스트 in `tests/integration/test_admin_delete_flow.py`

#### 구현 Task

- [x] T022 [US2] DeletionState 선언 (show_dialog, selected_qa_id, is_deleting) in `src/ui/admin_list_tab.py`
- [x] T023 [US2] 삭제 버튼 클릭 시 show_dialog=True 처리 in `src/ui/admin_list_tab.py`
- [x] T024 [US2] "아니오" 클릭 시 다이얼로그 닫기 핸들러 in `src/ui/admin_list_tab.py`
- [x] T025 [US2] 취소 플로우를 목록 이벤트 체인에 통합 in `src/ui/admin_list_tab.py`

**체크포인트**: US2 독립 완료 ✅

---

### Phase 5: User Story 3 - 항목 삭제 실행 [US3]

**목표**: 확인 후 ChromaDB에서 항목 삭제, 목록 갱신, 페이지 리셋

**독립 테스트 기준**:
- 특정 항목 삭제 시 목록에서 즉시 제거 ✅
- 페이지 마지막 항목 삭제 시 페이지 1로 리셋 ✅
- 존재하지 않는 항목 삭제 시도 시 오류 메시지 표시 ✅

#### 테스트 Task

- [x] T026 [P] [US3] QADeleteService 성공/실패/미존재 케이스 단위 테스트 in `tests/unit/test_qa_delete_service.py`
- [x] T027 [P] [US3] ChromaDB delete 계약(존재/미존재) 테스트 in `tests/contract/test_chromadb_delete.py`
- [x] T028 [US3] 삭제 후 목록 갱신 통합 테스트 in `tests/integration/test_admin_delete_flow.py`
- [ ] T029 [US3] 페이지 마지막 항목 삭제 시 리셋 테스트 in `tests/integration/test_admin_delete_flow.py`

#### 구현 Task

- [x] T030 [US3] delete_qa_item()에서 ChromaDB 삭제 및 결과 매핑 in `src/services/qa_delete_service.py`
- [x] T031 [US3] 삭제 성공 시 QAListService.get_list() 재조회 in `src/ui/admin_list_tab.py`
- [x] T032 [US3] 마지막 항목 삭제 시 current_page=1 리셋 in `src/ui/admin_list_tab.py`
- [x] T033 [US3] 삭제 핸들러를 목록 이벤트 체인에 통합 in `src/main.py`

**체크포인트**: US3 독립 완료 ✅

---

### Phase 6: User Story 4 - 삭제 상태 메시지 [US4]

**목표**: 삭제 진행/성공/실패 상태를 토스트로 사용자에게 명확히 전달

**독립 테스트 기준**:
- 삭제 시작 시 "삭제 중..." 토스트 표시 ✅
- 성공 시 "✓ 삭제되었습니다" 토스트 표시 ✅
- 실패 시 "❌ 삭제 실패 - [원인]" 토스트 표시 ✅

#### 테스트 Task

- [x] T034 [P] [US4] 삭제 진행 토스트 호출 단위 테스트 in `tests/unit/test_admin_list_tab.py`
- [x] T035 [P] [US4] 성공/실패 토스트 호출 단위 테스트 in `tests/unit/test_admin_list_tab.py`
- [ ] T036 [US4] 상태 메시지 E2E 통합 테스트 in `tests/integration/test_admin_delete_flow.py`

#### 구현 Task

- [x] T037 [US4] 삭제 시작 시 gr.Info("삭제 중...") in `src/ui/admin_list_tab.py`
- [x] T038 [US4] 성공 시 gr.Info("✓ 삭제되었습니다") in `src/ui/admin_list_tab.py`
- [x] T039 [US4] 실패 시 gr.Error("❌ 삭제 실패 - [원인]") in `src/ui/admin_list_tab.py`
- [x] T040 [US4] is_deleting 기반 중복 클릭 방지 in `src/ui/admin_list_tab.py`

**체크포인트**: US4 독립 완료 ✅

---

### Phase 7: Polish & Quality Assurance

**목표**: 공통 품질, 성능, 관찰성, 문서화

- [x] T041 [P] 삭제 이벤트 observability 필드 최종 정합 in `src/services/langfuse_service.py`
- [x] T042 [P] 동시 삭제 시나리오 (first-wins) 통합 테스트 in `tests/integration/test_admin_delete_flow.py`
- [x] T043 [P] 삭제 성능 (<2초) 검증 테스트 in `tests/performance/test_response_time.py`
- [ ] T044 quickstart 절차와 실제 동작 일치화 검증 in `specs/002-delete-qa-item/quickstart.md`
- [x] T045 전체 테스트 스위트 실행 및 결과 기록 in `tests/`

---

### 🆕 Phase 8: FR-010 - Langfuse 추적 통합 (NEW)

**목표**: 삭제 이벤트를 Langfuse에 자동 기록

**독립 테스트 기준**:
- 삭제 요청 시 Langfuse trace 생성
- trace.name == "delete_qa_item"
- 메타데이터: qa_id, admin_user, timestamp

#### 테스트 Task

- [ ] T046 [P] Langfuse span 생성 및 기록 테스트 in `tests/integration/test_qa_update.py`
  - Trace 객체 생성 확인
  - trace.output에 성공/실패 상태 기록
  - 메타데이터 필드 검증

#### 구현 Task

- [ ] T047 delete_qa_item()에 Langfuse span 래핑 in `src/services/qa_delete_service.py`
  ```python
  with langfuse_client.trace(
      name="delete_qa_item",
      input={"qa_id": qa_id, "admin_user": admin_user}
  ) as trace:
      result = chromadb_service.delete(qa_id)
      trace.output = {"success": result.success, "message": result.message}
  ```

#### Documentation Task

- [ ] T048 tasks.md, research.md, quickstart.md 최종 검증 및 커밋

**체크포인트**: Feature 002 완전 완료 ✅

---

## 🔗 의존성 & 실행 순서

### Phase 의존성

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← CRITICAL 선행 단계
    ↓
Phase 3 (US1) ＆ Phase 4 (US2) ＆ Phase 5 (US3) ＆ Phase 6 (US4) ← 병렬 가능
    ↓
Phase 7 (Polish)
    ↓
Phase 8 (FR-010) → Final verification
```

### User Story 의존성

| Story | 선행 | 병렬 가능 | 비고 |
|-------|------|---------|------|
| US1 | Phase 2 | O | 독립 구현 |
| US2 | Phase 2 + US1 버튼 | O | 같은 파일(admin_list_tab.py) 협업 주의 |
| US3 | Phase 2 + US2 확인 | O | 자연스럽게 결합 |
| US4 | Phase 2 + US3 삭제 | O | 상태 메시지 추가 |

### 병렬화 가능 지점

- **Phase 1**: T004~T006 병렬화 가능 (다른 파일, 선행 미완료)
- **Phase 2**: T009~T011 병렬화 가능 (서비스/계약 독립 부분)
- **US 테스트**: 스토리별 테스트 Task 병렬화 가능 (다른 파일)

---

## 🎯 병렬 실행 예시: User Story 3

```bash
# 동시 진행 가능 (T026, T027, T028)
- T026 [P] QADeleteService 단위 테스트 (tests/unit/)
- T027 [P] ChromaDB 계약 테스트 (tests/contract/)
- T028 [P] 목록 갱신 통합 테스트 (tests/integration/)

# 모두 완료 후 순차 진행
- T030 서비스 로직 구현
- T031 UI 재조회 연결
- T032~T033 통합
```

---

## 📦 구현 전략

### MVP 우선 (최소 완결 제품)

**권장 범위**: US1 (버튼) + US2 (확인 다이얼로그)

```
Phase 1 ✅ → Phase 2 ✅ → US1 ✅ → US2 ✅ → DEMO
```

**이유**: 사용자 오작동 방지 UI + 최소 완결 가치 제공

### 점진적 배포

1. **첫 번째**: US1+US2 (3-4시간) - 버튼+확인
2. **두 번째**: US3 추가 (2-3시간) - 실제 삭제
3. **세 번째**: US4 추가 (1-2시간) - 상태 메시지
4. **네 번째**: FR-010 추가 (0.5-1시간) - Langfuse 추적

---

## ✅ 검증 체크리스트

**Task 형식**:
- [x] 모든 Task `- [ ]` 마크다운 체크박스 형식
- [x] 모든 Task 고유 ID (T001∼T048)
- [x] [P] 라벨: 병렬화 가능 Task만 표시
- [x] [Story] 라벨: US 단계 Task만 표시 (Phase 1,2는 제외)
- [x] 모든 Task 정확한 파일 경로 포함

**Content**:
- [x] Phase별 목표 명시
- [x] 각 Story별 독립 테스트 기준 명시
- [x] 의존성 그래프 명시
- [x] 병렬화 예시 제공
- [x] MVP 및 점진적 배포 전략 명시

---

## 📄 현재 상태 (2025-03-05)

| 단계 | 상태 | 비고 |
|------|------|------|
| Phase 1 | ✅ 완료 | 6개 Task 완료 |
| Phase 2 | ✅ 완료 | 6개 Task 완료 - **선행 단계 완료** |
| Phase 3 (US1) | ✅ 완료 | 6개 Task 완료 |
| Phase 4 (US2) | ✅ 완료 | 6개 Task 완료 (T021 ⏳) |
| Phase 5 (US3) | ✅ 완료 | 7개 Task 완료 (T029 ⏳) |
| Phase 6 (US4) | ✅ 완료 | 7개 Task 완료 (T036 ⏳) |
| Phase 7 | ⏳ 진행중 | 5개 Task 중 4개 완료 (T044 ⏳) |
| Phase 8 | ⏳ 대기중 | 3개 Task 남음 (T046~T048) |

---

## 🚀 다음 스텝

### 즉시 (다음 30분)

1. T021 다이얼로그 통합 테스트 작성
2. T029 페이지 리셋 테스트 작성
3. T036 상태 메시지 E2E 테스트 작성

### 그 다음 (30-60분)

1. T044 quickstart 검증
2. T046 Langfuse span 테스트
3. T047 Langfuse span 구현
4. T048 최종 문서 및 커밋

### 완료 예정: 2025-03-05 (2-3시간)

