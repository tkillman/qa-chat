# Contract: QA Delete Service

## Method
`delete_qa_item(request: QADeleteRequest) -> QADeleteResult`

## Preconditions
- 관리자 인증은 상위 레이어에서 완료됨
- `request` 필수 필드 검증 통과

## Success Contract
- ChromaDB에서 `qa_id` 삭제 성공
- `QADeleteResult.success = true`
- UI는 목록 재조회 및 성공 toast 표시

## Failure Contract
- 삭제 실패 시 `success = false`
- 원인 분류 코드(`error_reason`) 포함
- UI는 오류 toast 표시

## Observability Contract
- Langfuse span 기록 필수
- 필수 속성: `qa_id`, `admin_user`, `success`, `error_reason`, `latency_ms`
