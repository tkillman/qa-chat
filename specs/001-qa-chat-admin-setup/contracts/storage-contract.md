# Contract: Storage and Data Synchronization

## Scope
`init.txt`(JSONL)와 ChromaDB 간 데이터 동기화 계약을 정의한다.

## File Contract: `data/init.txt`
- Format: JSONL (line-delimited JSON)
- Per-line schema:
```json
{"question":"<string>","answer":"<string>"}
```
- Validation:
  - `question` length `1..500`
  - `answer` length `1..2000`
  - malformed line은 skip하고 오류 로그를 남긴다.

## Startup Load Contract (`FR-001`)
- Trigger: 앱 시작 시 1회
- Behavior:
  - `init.txt` 각 유효 레코드를 읽어 ChromaDB에 반영
  - 파일 부재 시 빈 상태로 시작 (fatal 아님)
  - 로드 결과(건수/소요시간/성공여부)를 로그로 남김

## Update Sync Contract (`FR-003`, `FR-008`)
- Trigger: 관리자 업데이트 버튼 클릭
- Behavior:
  1. 입력 검증(길이/공백)
  2. ChromaDB upsert (정규화 질문 기준 중복 덮어쓰기)
  3. `init.txt`에도 동일 값 반영
- Consistency rule:
  - 성공 응답 이후에는 파일/벡터 저장소가 동일한 최신 답변을 보여야 한다.

## Search Contract (`FR-004`, `FR-005`)
- Query path: 사용자 질문 → ChromaDB 유사도 검색
- Matching rule:
  - 임계값: 0.7
  - 반환 개수: 1
- Fallback rule:
  - 미일치 시 정확히 `답변을 찾을 수 없습니다` 반환

## Embedding Contract (`FR-013`)
- Embedding provider: ChromaDB 기본 임베딩 함수
- 별도 외부 임베딩 API 의존 없음

## Observability Contract (`FR-006`)
- 이벤트: startup load, admin login, admin logout, qa update, user search, error
- 최소 필드: `event_type`, `success`, `duration_ms`(가능 시), `error_message`(오류 시)

## Implementation Checklist
- [x] `init.txt` malformed line skip + 경고 로그
- [x] startup load 결과(건수/시간/성공여부) 로깅
- [x] update 시 ChromaDB + 파일 반영 경계 처리(파일 실패 시 ChromaDB 롤백)
- [x] search top-1 + threshold 0.7 + 미검색 문구 고정
- [x] 임베딩 제공자 기본값 `chromadb_default`
