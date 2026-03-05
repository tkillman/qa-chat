# Feature Specification: Q&A 항목 삭제 기능

**Feature Branch**: `002-delete-qa-item`  
**Created**: 2026-03-05  
**Status**: Ready for Planning  
**Input**: User description: "관리자 목록 조회에서 Q&A 항목 삭제 기능: 각 행마다 삭제 버튼 추가, 클릭 시 확인 다이얼로그 표시 후 삭제 실행"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - 목록에 삭제 버튼 표시 (Priority: P1)

관리자가 "목록 조회" 탭의 테이블 각 행 오른쪽에 삭제 버튼(🗑️)이 표시되어야 합니다.

**Why this priority**: 삭제 기능의 기본 진입점이며, 버튼이 없으면 기능을 사용할 수 없습니다.

**Independent Test**: 관리자 로그인 → "목록 조회" 탭 진입 → 테이블 각 행에 삭제 버튼 확인

**Acceptance Scenarios**:

1. **Given** 관리자가 목록 조회 탭에 진입, **When** 1개 이상의 Q&A 항목이 표시될 때, **Then** 각 항목마다 삭제 버튼이 보임
2. **Given** Q&A 목록이 비어있을 때, **When** 목록 조회 탭 진입, **Then** 삭제 버튼이 표시되지 않음

---

### User Story 2 - 삭제 확인 다이얼로그 표시 (Priority: P1)

삭제 버튼 클릭 시 "이 항목을 삭제하시겠습니까?" 라는 확인 메시지를 보여야 합니다.

**Why this priority**: 실수로 삭제되는 것을 방지하기 위한 필수 안전장치입니다.

**Independent Test**: 삭제 버튼 클릭 → 확인 다이얼로그 표시 → "취소" 클릭 시 닫힘 확인

**Acceptance Scenarios**:

1. **Given** 삭제 버튼을 클릭했을 때, **When** 다이얼로그가 표시될 때, **Then** "예"와 "아니오" 옵션이 있음
2. **Given** 확인 다이얼로그가 표시되었을 때, **When** "아니오" 클릭, **Then** 다이얼로그가 닫히고 삭제되지 않음
3. **Given** 확인 다이얼로그가 표시되었을 때, **When** 다이얼로그 외부 클릭, **Then** 다이얼로그가 닫히고 삭제되지 않음

---

### User Story 3 - 항목 삭제 실행 (Priority: P1)

확인 다이얼로그에서 "예" 선택 시 ChromaDB에서 항목을 삭제하고 목록을 새로고침합니다.

**Why this priority**: 핵심 기능입니다. 삭제가 실제로 처리되어야 합니다.

**Independent Test**: 관리자 로그인 → 목록에서 특정 항목 확인 → 삭제 버튼 클릭 → "예" 선택 → 목록에서 항목 제거 확인

**Acceptance Scenarios**:

1. **Given** 삭제 확인 다이얼로그가 표시되었을 때, **When** "예" 클릭, **Then** 항목이 ChromaDB에서 삭제됨
2. **Given** 항목이 삭제되었을 때, **When** 삭제 후, **Then** 목록이 자동으로 갱신되어 해당 항목이 보이지 않음
3. **Given** 목록이 첫 번째 페이지의 마지막 항목(페이지당 10개)이 삭제되었을 때, **When** 삭제되면, **Then** 페이지가 1로 리셋됨

---

### User Story 4 - 삭제 상태 메시지 표시 (Priority: P2)

삭제 중일 때 "삭제 중..." 메시지를 표시하고, 완료 후 "✓ 삭제되었습니다" 또는 오류 메시지를 표시합니다.

**Why this priority**: 사용자 경험 개선. 작업 상태를 명확히 전달합니다.

**Independent Test**: 삭제 버튼 클릭 → "예" 선택 → 상태 메시지 확인

**Acceptance Scenarios**:

1. **Given** 삭제가 시작되었을 때, **When** 삭제 진행 중, **Then** "삭제 중..." 메시지 표시 또는 버튼 비활성화
2. **Given** 삭제가 완료되었을 때, **When** 정상 완료, **Then** "✓ 삭제되었습니다" 메시지 표시
3. **Given** 삭제 중 오류 발생했을 때, **When** 오류 발생, **Then** "❌ 삭제 실패했습니다" 메시지 표시

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 관리자 목록 조회 탭의 테이블 각 Q&A 항목 행에 삭제 버튼을 표시해야 함
- **FR-002**: 삭제 버튼 클릭 시 "이 항목을 삭제하시겠습니까?"라는 확인 요청 다이얼로그를 표시해야 함
- **FR-003**: 확인 다이얼로그에서 "예" 선택 시 ChromaDB에서 해당 Q&A 항목을 삭제해야 함
- **FR-004**: 항목 삭제 후 목록을 자동으로 갱신하여 삭제된 항목이 표시되지 않아야 함
- **FR-005**: 삭제 중 진행 상태를 화면 상단 toast 알림으로 표시해야 함 ("삭제 중...")
- **FR-006**: 삭제 완료 시 성공 메시지를 화면 상단 toast 알림으로 표시해야 함 ("✓ 삭제되었습니다", 3초 후 자동 소멸)
- **FR-007**: 삭제 실패 시 오류 메시지를 화면 상단 toast 알림으로 표시해야 함 ("❌ 삭제 실패했습니다 - [원인]")
- **FR-008**: 페이지 마지막 항목이 삭제될 경우, 페이지 번호를 1로 리셋하고 첫 페이지 데이터를 로드해야 함
- **FR-009**: 다이얼로그의 "아니오" 버튼 또는 외부 영역 클릭 시 다이얼로그를 닫고 삭제를 취소해야 함
- **FR-010**: 삭제 이벤트를 Langfuse에 span 형태로 기록하여 추적 가능해야 함

### Key Entities *(include if feature involves data)*

- **QADeleteRequest**: 삭제 요청을 나타내는 데이터 구조
  - `qa_id` (str): 삭제할 Q&A 항목의 고유 ID
  - `admin_user` (str): 삭제 요청한 관리자 사용자명
  - `timestamp` (datetime): 삭제 요청 시간

- **QADeleteResult**: 삭제 작업 결과를 나타내는 데이터 구조
  - `success` (bool): 삭제 성공 여부
  - `qa_id` (str): 삭제된 Q&A 항목 ID
  - `message` (str): 결과 메시지
  - `error_reason` (str, optional): 실패 시 오류 원인

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 관리자는 목록 조회에서 각 Q&A 항목의 삭제 버튼을 명확하게 식별할 수 있어야 함 (버튼 가시성 100%)
- **SC-002**: 삭제 버튼 클릭 후 1초 이내에 확인 다이얼로그가 표시되어야 함 (응답성 < 1초)
- **SC-003**: 중소 규모 데이터셋(~100개 항목)에서 삭제 완료 시간이 2초 이내여야 함 (성능 < 2초)
- **SC-004**: 삭제 후 목록이 자동으로 갱신되어 해당 항목이 완전히 제거되어야 함 (정확성 100%)
- **SC-005**: 삭제 실패 시 원인을 명확한 메시지로 사용자에게 전달해야 함 (오류 명확성 100%)
- **SC-006**: 모든 삭제 작업이 Langfuse에 기록되어 추적 가능해야 함 (감사 추적 100%)
- **SC-007**: 사용자가 2번 이상의 클릭 없이 삭제 작업을 취소할 수 있어야 함 (취소 편의성: "아니오" 또는 외부 클릭으로 즉시 취소)
- **SC-008**: 페이지 마지막 항목 삭제 시 페이지 번호가 자동으로 조정되어 오류가 발생하지 않아야 함 (안정성 100%)

## Edge Cases & Error Handling

- **EC-001**: 관리자가 삭제 중에 페이지를 새로고침하면? → 현재 삭제 작업 진행 상황을 유지하고 완료 후 목록 갱신
- **EC-002**: 동시에 두 명의 관리자가 같은 항목을 삭제하려고 시도하면? → 먼저 삭제한 관리자 성공, 두 번째 관리자에게 "항목을 찾을 수 없습니다" 오류 표시
- **EC-003**: 삭제 작업 중에 네트워크 연결이 끊어지면? → "네트워크 오류가 발생했습니다. 다시 시도하시겠습니까?" 메시지와 재시도 옵션 제공
- **EC-004**: ChromaDB가 일시적으로 응답하지 않으면? → 사용자 친화적 오류 메시지 표시 및 관리자가 나중에 재시도할 수 있도록 함
- **EC-005**: 목록에 항목이 1개만 있을 때 삭제하면? → 삭제 후 빈 상태 메시지 표시
- **EC-006**: 페이지 2에서 마지막 항목을 삭제하면? → 페이지가 1로 리셋되고 첫 페이지 항목 표시
- **EC-007**: 삭제 버튼을 빠르게 여러 번 클릭하면? → 버튼을 비활성화하여 중복 삭제 방지

## Assumptions

- 관리자는 항상 유효한 인증 상태에 있다고 가정
- ChromaDB 컬렉션에 저장된 Q&A 항목의 ID는 고유하고 불변이라고 가정
- 각 페이지는 10개의 항목을 고정 표시한다고 가정
- Langfuse 서비스는 이용 가능하거나 사용 불가능해도 삭제는 진행된다고 가정
- 삭제 요청은 즉시 처리되며, 비동기 배치 처리가 아니라고 가정

## Clarifications

### Session 2026-03-05

- Q: Q&A 항목 식별 방식은? → A: 질문 텍스트 기반 Hash ID (QAItem.get_hash_key() 사용)
- Q: 삭제 버튼 UI 배치 위치는? → A: 테이블의 작업 컬럼 우측 정렬, 항상 표시
- Q: 상태 메시지 표시 방식은? → A: 화면 상단 toast 알림 (Gradio gr.Info/gr.Error, 3초 자동 소멸)
- Q: 삭제 권한 검증 수준은? → A: 관리자 인증만 확인 (이미 로그인 상태에서만 접근 가능)
- Q: 동시 삭제 요청 처리는? → A: Optimistic 패턴 (먼저 성공, 두 번째는 "항목 없음" 오류)
- Q: 삭제 UX는 확인 다이얼로그를 유지할지? → A: 확인 다이얼로그 유지 ("예/아니오" 후 삭제)
- Q: 페이지당 표시 항목 수는? → A: 페이지당 10개 고정
- Q: 목록 표시 UI 형태는? → A: 테이블 UI 고정 (질문/답변/작업 컬럼)

## Out of Scope

- 확인 없이 즉시 삭제 실행 UX
- 삭제된 항목의 복구(undo/redo) 기능
- 삭제 이력 대시보드 (감사 로그 조회는 별도 기능)
- 대량 일괄 삭제 기능
- 항목 아카이빙 기능
