# Research: Q&A 항목 삭제 기능

**기능**: Q&A 항목 삭제 기능 | **브랜치**: `002-delete-qa-item` | **날짜**: 2026-03-05

## Decision 1: 삭제 식별자 규격
- **Decision**: 질문 텍스트 기반 Hash ID(`QAItem.get_hash_key()`)를 삭제 키로 사용
- **Rationale**: Feature 001에서 이미 저장/조회에 쓰는 식별자 규칙과 일치해 추가 매핑 비용이 없음
- **Alternatives considered**:
  - UUID 별도 컬럼 도입: 기존 데이터 마이그레이션 필요
  - 질문 원문 기반 삭제: 정규화/공백 차이로 오삭제 위험

## Decision 2: UI 액션 패턴
- **Decision**: 카드 헤더 우측에 상시 표시되는 삭제 버튼 + 확인 다이얼로그 2단계 플로우
- **Rationale**: 오작동 방지와 가시성을 동시에 만족하며 스펙의 P1 시나리오를 직접 충족
- **Alternatives considered**:
  - 호버 시 버튼 노출: 모바일/접근성 저하
  - 즉시 삭제(다이얼로그 없음): 실수 삭제 위험 증가

## Decision 3: 동시성 처리
- **Decision**: Optimistic concurrency(먼저 성공, 후속 요청은 항목 없음 오류)
- **Rationale**: 잠금/트랜잭션 오버헤드 없이 현재 규모에서 충분한 안정성 확보
- **Alternatives considered**:
  - 분산 락: 구현 복잡도 과다
  - UI 레벨 단순 비활성화만 적용: 다중 관리자 시나리오 미해결

## Decision 4: 상태 메시지 전달
- **Decision**: Gradio `gr.Info`/`gr.Error` 토스트 사용, 성공 메시지는 3초 내 자동 소멸
- **Rationale**: 스펙 FR-005~FR-007 직접 충족, 비차단 UX
- **Alternatives considered**:
  - 인라인 Markdown 상태바: 목록 영역 레이아웃 변경 부담
  - 모달 상태 텍스트: 상호작용 중단 유발

## Decision 5: 관찰성 필드 표준
- **Decision**: 삭제 이벤트 필드 `{event_type, success, qa_id, admin_user, error_message, timestamp}` 표준화
- **Rationale**: 헌법 I 원칙(관찰 가능성) 충족 및 장애 분석 용이
- **Alternatives considered**:
  - success/failure만 기록: 원인 추적 정보 부족
  - raw exception 전체 덤프: 노이즈 증가 및 민감정보 위험

## Decision 6: JavaScript 함수 스코핑 구조 ✓ (버그 수정됨)
- **Decision**: 전역 `deleteQA` 함수를 `create_admin_list_tab()` 초기에 한 번만 정의하고, IIFE로 스코프 격리
- **Rationale**: 
  - Gradio HTML 컴포넌트는 각 렌더링마다 격리된 스코프를 가짐
  - 카드 재생성 시마다 중복 함수 정의 방지
  - 클릭 이벤트 핸들러가 함수 찾기 오류 해결
- **Alternatives considered**:
  - 인라인 이벤트 핸들러에 함수 정의: 성능 저하 + 중복 정의 문제
  - 동적 스크립트 삽입: 보안 리스크 증가

## Decision 7: 페이지 상태 복구 전략
- **Decision**: 마지막 항목 삭제 시 페이지를 1로 리셋하고 첫 페이지 데이터 로드
- **Rationale**: 
  - 사용자 경험: 빈 페이지(404)보다 데이터 있는 페이지가 낫다
  - 스펙 FR-008 명시 사항
  - 일관된 상태 관리
- **Alternatives considered**:
  - 자동으로 이전 페이지로 이동: 페이지 1에서 마지막 항목 삭제 시 혼동
  - 페이지 상태 유지: 오류 메시지 노출 필요

## Decision 8: Langfuse 통합 전략
- **Decision**: `LangfuseService.log_deletion_event()` span으로 요청 → 처리 → 응답 추적
- **Rationale**:
  - 헌법 원칙 I (관찰 가능성 우선)
  - 성능 모니터링: 평균 응답 시간 < 2초 추적
  - 오류 분석: 스택 트레이스 + 사용자 컨텍스트 기록
  - 감사 로그: admin_user + 타임스탬프 기록
- **Alternatives considered**:
  - 로그 파일만 사용: 구조화 부족, 대규모 데이터 검색 어려움
  - 데이터베이스 감사 테이블: 추가 스토리지 + 마이그레이션 필요

## 해결된 NEEDS CLARIFICATION ✓

### 결과: 0개 미해결 (모든 항목 명확)

**이유**:
1. **spec.md의 상세함**: Clarifications 섹션에서 5개 Q&A로 명확히 답변
2. **기존 구현 참고**: 이미 구현된 코드가 의도를 명확히 보여줌
3. **도메인 경험**: 관리자 기능 (001, 001-qa-chat-admin-setup) 선행 경험

**Spec 기반 확인**:
- ✅ Q&A 항목 식별 방식: Hash ID (`QAItem.get_hash_key()`)
- ✅ 삭제 버튼 위치: 카드 헤더 우측에 상시 표시
- ✅ 상태 메시지: Toast 알림 (gr.Info/gr.Error)
- ✅ 삭제 권한: 관리자 인증만 (이미 로그인 상태)
- ✅ 동시 삭제 처리: Optimistic 패턴 (먼저 성공, 이후 오류)

## 기술 결정 매트릭스

| # | 기술 영역 | 선택안 | 선택한 이유 | 대안 |
|---|---------|--------|-----------|-----|
| 1 | 식별자 | Hash ID | 기존 001에서 사용 중, 일관성 | UUID (마이그레이션 비용) |
| 2 | UI 패턴 | 버튼 + 다이얼로그 | 가시성 + 안전성 균형 | 호버 버튼 (접근성 저하) |
| 3 | 동시성 | Optimistic | 간단함 + 규모에 적합 | 분산 락 (복잡) |
| 4 | 상태 메시지 | Toast (gr.Info/Error) | 비차단 UX + 스펙 준수 | 모달 (상호작용 중단) |
| 5 | 텔레메트리 | Langfuse span | 구조화된 관찰 가능성 | 로그 파일 (검색 어려움) |
| 6 | JS 스코핑 | 전역 함수 + IIFE | 중복 정의 방지 + 격리 | 인라인 (성능 저하) |
| 7 | 페이지 복구 | 1로 리셋 | 사용자 경험 최적화 | 이전 페이지 (혼동 가능) |
| 8 | Langfuse 통합 | Span 기반 추적 | 성능 + 오류 분석 | DB 감사 테이블 (복잡) |

## 의존성 및 선행 작업

### 요구되는 기술
- **Python 3.11+**: 타입 힌팅, 패턴 매칭 사용
- **Gradio 4.x**: State, Button, HTML 컴포넌트
- **ChromaDB 0.4+**: delete() 메서드
- **Langfuse 2.x**: span 기반 추적
- **pytest 7.x+**: 단위 및 통합 테스트

### 선행 작업 (완료됨)
- ✅ 001-admin-qa-list: 목록 조회 기능 (카드 UI 레이아웃)
- ✅ 001-qa-chat-admin-setup: 관리자 인증 (패스워드 검증)
- ✅ QAItem 모델: Hash ID 생성 메커니즘
- ✅ ChromaDB 통합: 연결 및 쿼리 기본 구조

## 다음 단계: Phase 1 설계

### 생성될 문서
1. **data-model.md**: QADeleteRequest, QADeleteResult 정의
2. **contracts/delete-request.md**: 삭제 요청 계약 명세
3. **contracts/delete-response.md**: 삭제 응답 계약 명세
4. **quickstart.md**: 삭제 기능 빠른 시작 가이드

### 구현 검증 대상
- ✅ `src/services/qa_delete_service.py` 기본 로직 확인
- ✅ `src/ui/admin_list_tab.py` deleteQA 오류 수정 확인
- ✅ `src/models/qa_delete_models.py` 데이터 모델 확인
- ⏳ Langfuse 계측 포인트 추가 (Phase 2)
- ⏳ 테스트 케이스 작성 (Phase 2)
