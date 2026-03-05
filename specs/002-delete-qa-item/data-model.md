# Data Model: Q&A 항목 삭제 기능

## 1) QADeleteRequest

삭제 요청 입력 모델.

| Field | Type | Required | Rules |
|---|---|---:|---|
| `qa_id` | `str` | Y | 빈 문자열 불가, 공백-only 불가 |
| `admin_user` | `str` | Y | 빈 문자열 불가 |
| `timestamp` | `datetime` | Y | 생성 시 UTC 시각 |

### Validation
- `qa_id`가 비어 있으면 요청 거부
- `admin_user`가 비어 있으면 요청 거부

## 2) QADeleteResult

삭제 결과 모델.

| Field | Type | Required | Rules |
|---|---|---:|---|
| `success` | `bool` | Y | 성공/실패 플래그 |
| `qa_id` | `str` | Y | 요청 `qa_id`와 동일 |
| `message` | `str` | Y | 사용자 표시 메시지 |
| `error_reason` | `str \| None` | C | 실패 시 필수, 성공 시 `None` |
| `timestamp` | `datetime` | Y | 완료 시각 |

### Error Reasons (normalized)
- `not_found`
- `db_connection_error`
- `db_operation_error`
- `network_error`
- `timeout`
- `permission_denied`
- `unknown_error`

## 3) DeletionState (UI)

확인 다이얼로그/삭제 진행 상태 추적용 UI 상태.

| Field | Type | Default | Meaning |
|---|---|---|---|
| `show_dialog` | `bool` | `False` | 확인 다이얼로그 표시 여부 |
| `selected_qa_id` | `str \| None` | `None` | 선택된 대상 ID |
| `selected_question_preview` | `str \| None` | `None` | UI 표시용 질문 미리보기 |
| `is_deleting` | `bool` | `False` | 삭제 처리 중 상태 |

## 4) State Transitions

1. `idle` → (삭제 버튼 클릭) → `dialog_open`
2. `dialog_open` → (`아니오`/외부 클릭) → `idle`
3. `dialog_open` → (`예`) → `deleting`
4. `deleting` → (성공) → `idle` + 목록 재조회
5. `deleting` → (실패) → `dialog_open` 또는 `idle`(정책에 따라)

## 5) Pagination Rule

- 페이지 크기: **10개 고정**
- 현재 페이지의 마지막 항목 삭제 후 비어 있으면: **페이지 1로 리셋 후 재조회**

## 6) Observability Fields (Langfuse)

삭제 span에 다음 속성을 기록한다.

- `event_type = qa_delete`
- `qa_id`
- `admin_user`
- `success`
- `error_reason` (실패 시)
- `latency_ms`
- `timestamp`
