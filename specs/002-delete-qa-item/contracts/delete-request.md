# Contract: Delete Request

## Interface
- Service: `QADeleteService`
- Method: `delete_qa_item(request: QADeleteRequest) -> QADeleteResult`

## Request Schema

```json
{
  "qa_id": "string",
  "admin_user": "string",
  "timestamp": "datetime (UTC)"
}
```

## Validation Rules
- `qa_id`는 빈 값 불가
- `admin_user`는 빈 값 불가
- `timestamp`는 요청 생성 시각(UTC)

## Semantics
- `qa_id`는 ChromaDB 문서 식별자로 사용
- 동일 `qa_id` 동시 삭제는 first-wins(후행 요청 not_found)
