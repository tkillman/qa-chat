# API 계약: 삭제 응답

**기능**: Q&A 항목 삭제 기능 | **계약**: 삭제 작업 응답 | **날짜**: 2026-03-05

## 개요

이 문서는 Q&A 항목 삭제 작업이 반환하는 응답의 구조를 정의합니다. 모든 삭제 시도는 성공/실패 여부와 상관없이 이 응답 구조를 따릅니다.

---

## 응답 구조

### 엔드포인트 (개념적)

```
Service: QADeleteService
Returns: QADeleteResult(
    success: bool,
    qa_id: str,
    message: str,
    error_reason: Optional[str],
    timestamp: datetime
)
```

---

## 필드 명세

### 필드 1: `success` (boolean) - 필수

**설명**: 삭제 작업의 성공 여부

**값**:
- `true`: 항목이 ChromaDB에서 성공적으로 삭제됨
- `false`: 삭제 실패 (원인은 error_reason 참조)

**검증**:
```python
# 항상 명시적으로 설정되어야 함
assert isinstance(success, bool)
```

**예시**:
```json
{
  "success": true,
  "qa_id": "abc123def456",
  "message": "✓ 삭제되었습니다"
}

{
  "success": false,
  "qa_id": "xyz789",
  "message": "항목을 찾을 수 없습니다",
  "error_reason": "not_found"
}
```

---

### 필드 2: `qa_id` (string) - 필수

**설명**: 처리 대상이었던 Q&A의 고유 ID

**형식**: 요청의 qa_id와 동일

**목적**:
- 요청-응답 매칭 (감사 추적)
- 여러 삭제 작업 간 구분
- Langfuse 기록에서 대상 항목 식별

**예시**:
```
"abc123def456"
```

**불변성**: 응답의 qa_id는 항상 요청의 qa_id와 정확히 같음

---

### 필드 3: `message` (string) - 필수

**설명**: 사용자에게 표시할 메시지 (Gradio toast 알림)

**형식**: 
- **성공 시**: 긍정적 메시지 (✓ 이모지 포함)
- **실패 시**: 실패 원인 설명 (❌ 이모지 포함)

**규칙**: 
- 90자 이내 (UI 표시용)
- HTML/마크다운 미포함 (평문만)
- 업적/손실 명확하게 표현

**예시**:

| 상황 | message | 표시 형태 |
|------|---------|---------|
| 성공 | `"✓ 삭제되었습니다"` | 3초 후 자동 소멸 (gr.Info) |
| 항목 없음 | `"항목을 찾을 수 없습니다"` | 3초 후 자동 소멸 (gr.Error) |
| 연결 오류 | `"데이터베이스 연결 오류"` | 3초 후 자동 소멸 (gr.Error) |

---

### 필드 4: `error_reason` (string \| null) - 조건부

**설명**: 오류 원인의 내부 분류 코드 (개발자/모니터링용)

**필수 조건**:
- `success=false`이면 반드시 설정
- `success=true`이면 반드시 `null`

**허용된 값** (열거형):

| 코드 | HTTP | 설명 | 샘플 메시지 | 재시도 가능 |
|------|:--:|------|:--|:--:|
| `not_found` | 404 | 항목이 존재하지 않음 | "항목을 찾을 수 없습니다" | ❌ |
| `permission_denied` | 403 | 관리자 권한 없음 | "권한이 없습니다" | ❌ |
| `db_connection_error` | 503 | DB 연결 불가 | "데이터베이스 연결 오류" | ✅ (재시도) |
| `db_operation_error` | 500 | DB 작업 실패 | "데이터베이스 작업 실패" | ✅ (재시도) |
| `network_error` | 0 | 네트워크 오류 | "네트워크 오류가 발생했습니다" | ✅ (재시도) |
| `timeout` | 408 | 요청 타임아웃 | "요청이 시간 초과되었습니다" | ✅ (재시도) |
| `unknown_error` | 500 | 예기치 않은 오류 | "알 수 없는 오류가 발생했습니다" | ✅ (재시도) |

**검증**:
```python
VALID_ERROR_REASONS = {
    "not_found", "permission_denied", "db_connection_error",
    "db_operation_error", "network_error", "timeout", "unknown_error"
}

if not success:
    assert error_reason in VALID_ERROR_REASONS
    assert error_reason is not None
else:
    assert error_reason is None
```

---

### 필드 5: `timestamp` (datetime) - 필수

**설명**: 작업 완료 시각 (UTC)

**형식**: ISO 8601 UTC  
예: `"2026-03-05T19:00:05Z"`

**계산**:
```
완료 시간 = now() 
처리 시간 = timestamp_response - timestamp_request
```

**성능 목표** (스펙 SC-003):
```
처리 시간 < 2초 (중소 규모 ~100개 항목)
```

**Langfuse 추적**:
```python
duration_ms = (result.timestamp - request.timestamp).total_seconds() * 1000
# span에 기록: duration < 2000ms 목표
```

---

## 응답 시나리오

### 시나리오 1: 성공

```python
QADeleteResult(
    success=True,
    qa_id="abc123def456",
    message="✓ 삭제되었습니다",
    error_reason=None,
    timestamp=datetime.utcnow()
)
```

**처리**:
1. 목록 자동 갱신 (해당 항목 제거)
2. Toast 알림 표시 (3초 후 자동 소멸)
3. 다이얼로그 닫고 초기 상태로 복귀

---

### 시나리오 2: 항목 없음 (Optimistic 동시성)

```python
QADeleteResult(
    success=False,
    qa_id="xyz789",
    message="항목을 찾을 수 없습니다",
    error_reason="not_found",
    timestamp=datetime.utcnow()
)
```

**상황**: 
- 항목이 이미 다른 관리자에 의해 삭제됨
- 또는 잘못된 ID로 요청됨

**처리**:
1. 오류 메시지 표시 (Toast, 3초 후 소멸)
2. 다이얼로그 닫기
3. 목록 상태 유지 (현재 페이지 유지)

---

### 시나리오 3: 데이터베이스 오류

```python
QADeleteResult(
    success=False,
    qa_id="abc123def456",
    message="데이터베이스 연결 오류",
    error_reason="db_connection_error",
    timestamp=datetime.utcnow()
)
```

**상황**: ChromaDB 연결 실패

**처리**:
1. 오류 메시지 표시 (Toast)
2. 다이얼로그 유지 (재시도 가능하도록)
3. "재시도" 옵션 제공 가능 (future enhancement)

---

### 시나리오 4: 네트워크 오류

```python
QADeleteResult(
    success=False,
    qa_id="abc123def456",
    message="네트워크 오류가 발생했습니다",
    error_reason="network_error",
    timestamp=datetime.utcnow()
)
```

**처리**:
1. 오류 메시지 표시
2. 다이얼로그 유지 (재시도 가능)
3. 사용자에게 재시도 제안

---

## 응답 특성

### 보장 사항

| 보장 | 설명 |
|------|------|
| **일관성** | success + error_reason 조합이 일의적 (success=true와 error_reason이 동시에 설정되지 않음) |
| **추적성** | message + error_reason으로 사건 분류 가능 |
| **결정성** | 같은 요청에 대해 항상 같은 결과 (멱등성, 단 항목 삭제 후는 "not_found") |
| **타임스탦프** | 정렬 가능 (감사 로그 용) |

### 제약사항

1. **단방향**: 응답은 요청에 대한 최종 결과 (재협상 불가)
2. **즉시성**: 삭제 후 즉시 ChromaDB에 반영됨 (비동기 없음)
3. **범위**: 목록 갱신은 응답 후 클라이언트에서 수행 (별도 API 호출)

---

## 통합 예제

### 요청 → 응답 사이클

```python
# 1️⃣ 요청 생성
request = QADeleteRequest(
    qa_id="abc123def456",
    admin_user="admin"
)

# 2️⃣ 서비스 호출
result = delete_service.delete_qa_item(request)

# 3️⃣ 응답 검사
if result.success:
    # ✅ 성공 경로
    gr.Info(result.message)  # "✓ 삭제되었습니다"
    # 목록 갱신
    refresh_list(page)
else:
    # ❌ 실패 경로
    if result.is_not_found():
        # 항목이 없음 → 재시도 불가
        gr.Error(result.message)
    elif result.is_retriable():
        # 네트워크 오류 → 재시도 제안
        gr.Error(result.message + " (재시도해주세요)")
    else:
        # 기타 오류
        gr.Error(result.message)
```

---

## Langfuse 기록

### Span 구조

```json
{
  "name": "qa_deletion",
  "input": {
    "qa_id": "abc123def456",
    "admin_user": "admin"
  },
  "output": {
    "success": true,
    "message": "✓ 삭제되었습니다",
    "error_reason": null
  },
  "metadata": {
    "duration_ms": 1250,
    "error_reason_tag": "success" | "not_found" | "db_error" | ...
  }
}
```

---

## 다음 단계

- ✅ contracts/delete-response.md (이 파일)
- ✅ contracts/delete-request.md (요청 명세)
- [data-model.md](../data-model.md) 참조
- [plan.md](../plan.md) 참조
