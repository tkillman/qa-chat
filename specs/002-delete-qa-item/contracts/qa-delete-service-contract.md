# Contract: QA Delete Service

## Interface
- Service: `QADeleteService`
- Method: `delete_qa_item(request: QADeleteRequest) -> QADeleteResult`

## Preconditions
- 관리자 인증은 UI 레이어에서 이미 통과한 상태
- `request.qa_id`/`request.admin_user`는 비어 있지 않아야 함

## Success Contract
- 반환값: `QADeleteResult(success=True, qa_id=<id>, message=<성공 메시지>, error_reason=None)`
- 부수효과:
  1. ChromaDB에서 `qa_id` 삭제
  2. Langfuse 삭제 이벤트 기록

## Failure Contract
- 반환값: `QADeleteResult(success=False, qa_id=<id>, message=<실패 메시지>, error_reason=<원인>)`
- 대표 오류 원인:
  - `항목을 찾을 수 없습니다` (이미 삭제됨/미존재)
  - `네트워크 오류`
  - `DB 오류`

## Concurrency Semantics
- Optimistic first-wins
- 동일 `qa_id`에 대해 선행 요청 성공 후 후행 요청은 not-found 실패

## Observability Fields
- `event_type=qa_deleted`
- `success`
- `qa_id`
- `admin_user`
- `error_message` (실패 시)
- `timestamp`
