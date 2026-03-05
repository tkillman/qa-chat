# Contract: Delete Response

## Response Schema

```json
{
  "success": "boolean",
  "qa_id": "string",
  "message": "string",
  "error_reason": "string|null",
  "timestamp": "datetime (UTC)"
}
```

## Rules
- 성공 시: `success=true`, `error_reason=null`
- 실패 시: `success=false`, `error_reason` 필수
- `qa_id`는 요청 `qa_id`와 동일

## Error Reasons
- `not_found`
- `db_connection_error`
- `db_operation_error`
- `network_error`
- `timeout`
- `permission_denied`
- `unknown_error`
