# Phase 0 Research: QA Chat 관리자 및 초기 설정

## Decision 1: 임베딩 함수는 ChromaDB 기본 함수를 사용한다
- Decision: 사용자/관리자 입력 임베딩 생성에 ChromaDB 기본 임베딩 함수를 사용한다.
- Rationale: 외부 API 의존 없이 로컬·Docker 환경에서 재현 가능하며, 운영 복잡도와 키 관리 부담이 낮다.
- Alternatives considered:
  - OpenAI Embeddings API: 품질 이점 가능성이 있으나 비용/네트워크 의존 증가로 제외.
  - sentence-transformers 직접 로딩: 제어성은 높지만 모델 배포/메모리 관리 비용 증가로 제외.

## Decision 2: 관리자 인증 상태는 전역 단일 상태로 유지한다
- Decision: 관리자 로그인 상태는 앱 전역 플래그 1개로 관리한다.
- Rationale: 명세 확정사항이며 구현 단순성이 높고 현재 범위(P1/P2)에 적합하다.
- Alternatives considered:
  - 세션별 인증 상태: 다중 사용자 격리에 유리하나 현재 확정 스펙과 상충.
  - 요청별 재인증: 보안은 강화되지만 UX/구현 복잡도 증가.

## Decision 3: 로그아웃은 명시적 UI 액션으로 제공한다
- Decision: 관리자 화면에 로그아웃 버튼을 제공하고 클릭 시 전역 로그인 상태를 해제한다.
- Rationale: 사용자 스토리 2 시나리오와 일치하며 테스트 가능한 종료 조건을 제공한다.
- Alternatives considered:
  - 로그아웃 미지원: 운영 중 상태 회수가 어려워 제외.
  - 타임아웃 전용 로그아웃: 스펙 범위를 넘어가므로 제외.

## Decision 4: 로그인 시도 잠금 정책은 적용하지 않는다
- Decision: 로그인 실패 횟수 제한/잠금을 두지 않는다.
- Rationale: 명세 확정사항(FR-012)으로 현재 MVP 흐름을 단순하게 유지한다.
- Alternatives considered:
  - 5회 실패 잠금: 보안성 향상 가능하지만 스펙 비합치.
  - 3회 실패 장기 잠금: 사용자 차단 리스크와 운영 복잡도 증가.

## Decision 5: 검색 미결과 문구를 단일 문자열로 고정한다
- Decision: 검색 결과가 없을 때 정확히 "답변을 찾을 수 없습니다"를 반환한다.
- Rationale: FR-005의 테스트 결정성을 높이고 UI/테스트/문서 간 불일치를 제거한다.
- Alternatives considered:
  - 장문 안내 문구: 친절성은 높으나 테스트 단일성 저하.
  - 문구 혼용: 회귀 테스트 및 계약 검증 어려움.

## Decision 6: 파일-벡터 저장 이중화 패턴을 유지한다
- Decision: `init.txt(JSONL)`를 소스 데이터로 유지하고 앱 시작 시 ChromaDB로 로드한다.
- Rationale: 재시작 내구성/백업 단순성이 높고 기존 코드 경로(`init_loader`, `file_service`)와 일치한다.
- Alternatives considered:
  - ChromaDB 단독 영속화: 단순해 보이지만 파일 기반 초기 데이터 관리 요구와 불일치.
  - RDBMS 추가: 현 범위를 초과하는 인프라 도입.

## Decision 7: 테스트는 기존 pytest 계층을 활용한다
- Decision: 단위/통합/계약 테스트를 `tests/` 계층에서 유지하고 기능별 회귀를 우선 실행한다.
- Rationale: 프로젝트에 이미 테스트 구조와 케이스가 존재해 확장 비용이 낮다.
- Alternatives considered:
  - UI E2E 신규 도입: 장기적으로 유용하지만 이번 계획 단계 범위를 초과.
  - 수동 테스트 전용: 헌법의 TDD 원칙과 충돌.

## Resolved Clarifications
- 관리자 인증 상태 범위: 전역 단일 상태
- 로그아웃 동작: 버튼 기반 전역 해제 + 로그인 화면 복귀
- 로그인 제한: 없음
- 임베딩 모델: ChromaDB 기본 함수
- 검색 미결과 문구: "답변을 찾을 수 없습니다"

모든 `NEEDS CLARIFICATION` 항목은 해결 완료.
