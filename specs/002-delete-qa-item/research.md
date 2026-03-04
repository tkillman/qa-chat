# Research: Q&A 항목 삭제 기능

## Decision 1: 삭제 식별자 규격
- Decision: 질문 텍스트 기반 Hash ID(`QAItem.get_hash_key()`)를 삭제 키로 사용
- Rationale: Feature 001에서 이미 저장/조회에 쓰는 식별자 규칙과 일치해 추가 매핑 비용이 없음
- Alternatives considered:
  - UUID 별도 컬럼 도입: 기존 데이터 마이그레이션 필요
  - 질문 원문 기반 삭제: 정규화/공백 차이로 오삭제 위험

## Decision 2: UI 액션 패턴
- Decision: 카드 헤더 우측에 상시 표시되는 삭제 버튼 + 확인 다이얼로그 2단계 플로우
- Rationale: 오작동 방지와 가시성을 동시에 만족하며 스펙의 P1 시나리오를 직접 충족
- Alternatives considered:
  - 호버 시 버튼 노출: 모바일/접근성 저하
  - 즉시 삭제(다이얼로그 없음): 실수 삭제 위험 증가

## Decision 3: 동시성 처리
- Decision: Optimistic concurrency(먼저 성공, 후속 요청은 항목 없음 오류)
- Rationale: 잠금/트랜잭션 오버헤드 없이 현재 규모에서 충분한 안정성 확보
- Alternatives considered:
  - 분산 락: 구현 복잡도 과다
  - UI 레벨 단순 비활성화만 적용: 다중 관리자 시나리오 미해결

## Decision 4: 상태 메시지 전달
- Decision: Gradio `gr.Info`/`gr.Error` 토스트 사용, 성공 메시지는 3초 내 자동 소멸
- Rationale: 스펙 FR-005~FR-007 직접 충족, 비차단 UX
- Alternatives considered:
  - 인라인 Markdown 상태바: 목록 영역 레이아웃 변경 부담
  - 모달 상태 텍스트: 상호작용 중단 유발

## Decision 5: 관찰성 필드 표준
- Decision: 삭제 이벤트 필드 `{event_type, success, qa_id, admin_user, error_message, timestamp}` 표준화
- Rationale: 헌법 I 원칙(관찰 가능성) 충족 및 장애 분석 용이
- Alternatives considered:
  - success/failure만 기록: 원인 추적 정보 부족
  - raw exception 전체 덤프: 노이즈 증가 및 민감정보 위험
