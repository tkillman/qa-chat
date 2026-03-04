# Phase 1 Data Model: QA Chat 관리자 및 초기 설정

## 1) Entity: QAItem
- Purpose: 질문-답변의 정본 레코드 (파일 저장 + 벡터 검색 원본)
- Fields:
  - `question: str` (required, unique key by normalized question)
  - `answer: str` (required)
  - `metadata: dict` (optional; source, updated_at 등)
- Validation Rules:
  - `question` length: `1..500`
  - `answer` length: `1..2000`
  - question normalization: trim + case-insensitive 비교 기준
- Relationships:
  - `init.txt` JSONL 한 줄 = QAItem 1개
  - ChromaDB document/metadata 1개와 1:1 대응
- State Transitions:
  - `new` → `persisted(file)` → `indexed(chromadb)`
  - 중복 question 입력 시 `persisted/indexed` 상태에서 `updated`로 전이 (덮어쓰기)

## 2) Entity: AdminAuthState
- Purpose: 관리자 인증 상태 (전역 단일 상태)
- Fields:
  - `is_authenticated: bool`
  - `last_login_at: datetime | None`
  - `last_logout_at: datetime | None`
- Validation Rules:
  - 초기값 `False`
  - 로그인 성공 시에만 `True`
  - 로그아웃 시 무조건 `False`
- Relationships:
  - Gradio 관리자 컴포넌트 visible 상태와 1:1 매핑
- State Transitions:
  - `logged_out` --(valid password)--> `logged_in`
  - `logged_in` --(logout click)--> `logged_out`
  - `logged_out` --(invalid password)--> `logged_out`

## 3) Entity: SearchRequest
- Purpose: 사용자 질의 처리 입력 모델
- Fields:
  - `question: str`
  - `requested_at: datetime`
- Validation Rules:
  - `question` length: `1..500`
  - 빈 문자열/공백-only 금지
- Relationships:
  - 1개의 SearchRequest는 최대 1개의 SearchResult를 생성

## 4) Entity: SearchResult
- Purpose: 사용자에게 반환되는 검색 결과
- Fields:
  - `answer: str`
  - `similarity: float`
  - `matched: bool`
- Validation Rules:
  - `matched=True`인 경우 `similarity >= 0.7`
  - `matched=False`인 경우 `answer == "답변을 찾을 수 없습니다"` 및 `similarity == 0.0`
- Relationships:
  - `SearchRequest`와 1:1

## 5) Entity: InitFileRecord (JSONL Contract View)
- Purpose: `init.txt` 저장/로드를 위한 직렬화 형태
- Fields:
  - `question: str`
  - `answer: str`
- Validation Rules:
  - 각 줄은 독립 JSON object
  - malformed line은 건너뛰고 로그 기록
- Relationships:
  - `InitFileRecord` ↔ `QAItem` 양방향 변환

## Cross-Entity Invariants
- 동일한 정규화 question은 시스템 전체에서 하나의 QAItem만 유지한다.
- 파일(`init.txt`)과 ChromaDB 인덱스는 업데이트 성공 시 동일한 최신 answer를 반영해야 한다.
- 관리자 인증 상태(`AdminAuthState`)가 `False`이면 업데이트 API(`add_or_update_qa`)는 거부 메시지를 반환해야 한다.
