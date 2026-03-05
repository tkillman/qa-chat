# Research: Q&A 항목 삭제 기능

**Feature**: 002-delete-qa-item  
**Date**: 2026-03-05

## Decision 1: 삭제 UX
- **Decision**: 확인 다이얼로그(`예/아니오`)를 유지한다.
- **Rationale**: 실수 삭제 방지 요구(FR-002, FR-009)와 일치한다.
- **Alternatives considered**:
  - 확인 없이 즉시 삭제: 빠르지만 오삭제 위험이 커서 제외(Out of Scope).

## Decision 2: 목록 UI 형태
- **Decision**: 관리자 목록은 테이블 UI(질문/답변/작업 컬럼)로 고정한다.
- **Rationale**: 삭제 버튼 위치를 고정해 DOM/이벤트 안정성을 높이고 관리 화면 가독성을 확보한다.
- **Alternatives considered**:
  - 카드 UI: 구조 유연성은 높으나 클릭/렌더링 문제 재발 가능성이 더 큼.
  - 카드/테이블 토글: 범위 확장으로 MVP 복잡도 증가.

## Decision 3: 페이지 정책
- **Decision**: 페이지당 10개 고정.
- **Rationale**: 기존 spec/테스트와 일치하고 페이지 리셋 규칙(FR-008) 검증이 명확하다.
- **Alternatives considered**:
  - 50개 고정: 조회 효율은 좋으나 현재 요구와 불일치.
  - 사용자 선택(10/50/100): 범위 외.

## Decision 4: 삭제 처리 규약
- **Decision**: Optimistic concurrency(선행 삭제 성공, 후행은 not_found 처리).
- **Rationale**: 다중 관리자 동시 삭제에서 단순하고 예측 가능한 동작을 제공한다.
- **Alternatives considered**:
  - 분산 락/강한 직렬화: 현재 규모 대비 과도한 복잡도.

## Decision 5: 상태 메시지
- **Decision**: `gr.Info`/`gr.Error` toast로 진행/성공/실패를 표시한다.
- **Rationale**: FR-005~FR-007 충족, 비차단 피드백 제공.
- **Alternatives considered**:
  - 인라인 상태바: 레이아웃 결합도 증가.

## Decision 6: 관찰 가능성(Langfuse)
- **Decision**: 삭제 시도마다 span 기록(`qa_id`, `admin_user`, `success`, `error_reason`, `latency_ms`).
- **Rationale**: 헌법 I(관찰 가능성 우선)와 FR-010을 동시에 충족한다.
- **Alternatives considered**:
  - 단순 로컬 로그: 운영 추적/집계 한계.

## Technical Context Clarifications

본 기능 계획에서 `NEEDS CLARIFICATION` 항목은 모두 해소되었다.

- 삭제 UX: 확인 다이얼로그 유지
- UI 형태: 테이블 고정
- 페이지당 항목 수: 10개 고정
- 동시 삭제 처리: Optimistic
- 추적 방식: Langfuse span
