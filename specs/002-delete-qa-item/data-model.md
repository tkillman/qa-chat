# 데이터 모델: Q&A 항목 삭제 기능

**기능**: Q&A 항목 삭제 기능 | **브랜치**: `002-delete-qa-item` | **날짜**: 2026-03-05

## 개요

이 문서는 Q&A 항목 삭제 기능에서 사용되는 핵심 데이터 모델을 정의합니다. 모든 모델은 Python 타입으로 구현되며, 명시적인 검증과 상태 전이를 제공합니다.

---

## 1. QADeleteRequest (삭제 요청)

**목적**: 관리자의 Q&A 삭제 요청을 표현하고 검증

### 필드 정의

```python
@dataclass
class QADeleteRequest:
    qa_id: str              # 삭제 대상 Q&A의 고유 ID (Hash 기반)
    admin_user: str         # 삭제를 요청한 관리자 사용자명
    timestamp: datetime     # 요청 시각 (자동 설정)
```

| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|:--:|------|------|
| `qa_id` | str | ✅ | 삭제할 Q&A의 Hash ID (QAItem.get_hash_key()) | `"abc123def456"` |
| `admin_user` | str | ✅ | 관리자 식별자 (감사/추적용) | `"admin"` |
| `timestamp` | datetime | ✅ | 요청 시각 (UTC, 자동 생성) | `2026-03-05T19:00:00Z` |

### 검증 규칙

```python
def validate(self) -> bool:
    # Rule 1: qa_id는 비어있지 않아야 함
    if not self.qa_id or not self.qa_id.strip():
        raise ValueError("qa_id는 비워둘 수 없습니다")
    
    # Rule 2: admin_user는 비어있지 않아야 함
    if not self.admin_user or not self.admin_user.strip():
        raise ValueError("admin_user는 비워둘 수 없습니다")
    
    return True
```

### 준수 사항

- ✅ **헌법 II (벡터 인식 데이터 계약)**: qa_id는 ChromaDB 문서 ID와 일치
- ✅ **헌법 I (관찰 가능성)**: timestamp로 Langfuse 추적 가능

---

## 2. QADeleteResult (삭제 결과)

**목적**: Q&A 삭제 작업의 결과를 일관되게 표현

### 필드 정의

```python
@dataclass
class QADeleteResult:
    success: bool                  # 삭제 성공 여부
    qa_id: str                     # 처리 대상 Q&A ID
    message: str                   # 사용자 친화적 메시지
    error_reason: Optional[str]   # 실패 사유 (내부 분류 코드)
    timestamp: datetime            # 완료 시각
```

| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|:--:|------|------|
| `success` | bool | ✅ | 삭제 성공 여부 | `True` / `False` |
| `qa_id` | str | ✅ | 작업 대상 Q&A ID | `"abc123def456"` |
| `message` | str | ✅ | UI에 표시할 메시지 (사용자 친화적) | `"✓ 삭제되었습니다"` |
| `error_reason` | str \| None | ❌ | 오류 분류 코드 (개발자용) | `"not_found"` |
| `timestamp` | datetime | ✅ | 작업 완료 시각 | `2026-03-05T19:00:05Z` |

### 검증 규칙

```python
def validate(self) -> bool:
    # Rule 1: message는 항상 필수
    if not self.message or not self.message.strip():
        raise ValueError("message는 비워둘 수 없습니다")
    
    # Rule 2: success=False이면 error_reason 필수
    if not self.success and not self.error_reason:
        raise ValueError("실패 시 error_reason은 필수입니다")
    
    # Rule 3: success=True이면 error_reason은 None이어야 함
    if self.success and self.error_reason:
        raise ValueError("성공 시 error_reason은 None이어야 합니다")
    
    return True

def is_not_found(self) -> bool:
    """항목이 없는 오류인지 확인"""
    return not self.success and self.error_reason == "not_found"

def is_retriable(self) -> bool:
    """재시도 가능한 오류인지 확인"""
    return not self.success and self.error_reason in [
        "database_connection_error",
        "database_operation_error", 
        "network_error",
    ]
```

### 준수 사항

- ✅ **헌법 III (사용자 중심 UI)**: message는 명확하고 친화적
- ✅ **헌법 I (관찰 가능성)**: error_reason으로 원인 분류 가능

---

## 3. DeletionState (UI 삭제 상태)

**목적**: Gradio State 컴포넌트에서 다이얼로그 및 삭제 진행을 추적

### 필드 정의

```python
@dataclass
class DeletionState:
    show_dialog: bool                      # 확인 다이얼로그 표시 여부
    selected_qa_id: Optional[str]         # 선택된 Q&A ID (None = 아무것도 선택 안 됨)
    selected_question_preview: Optional[str]  # 삭제 대기 중인 질문 미리보기
    is_deleting: bool                      # 삭제 진행 중 여부 (버튼 비활성화용)
```

| 필드 | 타입 | 기본값 | 설명 |
|------|:--:|:--:|------|
| `show_dialog` | bool | False | 다이얼로그 표시 여부 |
| `selected_qa_id` | str \| None | None | 선택된 항목 ID |
| `selected_question_preview` | str \| None | None | 질문 미리보기 텍스트 |
| `is_deleting` | bool | False | 삭제 중 여부 (진행 표시기용) |

### 상태 전이 다이어그램

```
┌──────────────────────────────┐
│ 1️⃣ 초기 상태 (idle)           │
│ show_dialog=False            │
│ selected_qa_id=None          │
│ is_deleting=False            │
└──────────────────────────────┘
            ↓
      [삭제 버튼 클릭]
      (deleteQA(qa_id))
            ↓
┌──────────────────────────────┐
│ 2️⃣ 확인 다이얼로그 열음        │
│ show_dialog=True             │
│ selected_qa_id=qa_id         │
│ selected_question_preview=텍스트│
│ is_deleting=False            │
└──────────────────────────────┘
      ↙              ↘
  ["예"]           ["아니오" / 외부 클릭]
    ↓                        ↓
    ↓              ┌──────────────────────────────┐
    ↓              │ 4️⃣ 취소됨 (idle로 복귀)      │
    ↓              │ show_dialog=False            │
    ↓              │ selected_qa_id=None          │
    ↓              │ is_deleting=False            │
    ↓              └──────────────────────────────┘
    ↓
┌──────────────────────────────┐
│ 3️⃣ 삭제 진행 중 (deleting)    │
│ show_dialog=True             │
│ selected_qa_id=qa_id         │
│ is_deleting=True  ← 버튼 비활성화│
└──────────────────────────────┘
            ↓
    [ChromaDB delete]
            ↓
       ┌────┴────┐
       ↓         ↓
   [성공]     [실패]
       ↓         ↓
    ┌──────┐  ┌──────┐
    │ 5️⃣   │  │ 6️⃣   │
    │ 성공  │  │ 오류  │
    └──────┘  └──────┘
       ↓         ↓
   [목록 갱신]  [오류 메시지]
       ↓         ↓  (재시도 옵션)
       └────┬────┘
            ↓
     ┌──────────────────┐
     │ idle로 복귀      │
     └──────────────────┘
```

### 상태 전이 메서드

```python
def open_dialog(self, qa_id: str, preview: str) -> 'DeletionState':
    """확인 다이얼로그 열기"""
    return DeletionState(
        show_dialog=True,
        selected_qa_id=qa_id,
        selected_question_preview=preview,
        is_deleting=False,
    )

def mark_deleting(self) -> 'DeletionState':
    """삭제 진행 시작"""
    return DeletionState(
        show_dialog=True,
        selected_qa_id=self.selected_qa_id,
        selected_question_preview=self.selected_question_preview,
        is_deleting=True,  # ← 버튼 비활성화
    )

def reset(self) -> 'DeletionState':
    """초기 상태로 복귀"""
    return DeletionState()
```

### 준수 사항

- ✅ **헌법 III (사용자 중심 UI)**: 상태 전이가 명확하고 사용자 오류 방지
- ✅ **스펙 FR-009**: "아니오" 클릭 시 상태 리셋

---

## 4. 오류 분류 코드 (error_reason)

결정된 오류 원인을 일관되게 분류

| 코드 | HTTP | 설명 | 사용자 메시지 | 재시도 | Langfuse 태그 |
|------|:--:|------|:--|:--:|:--|
| `not_found` | 404 | 항목이 존재하지 않음 | "항목을 찾을 수 없습니다" | ❌ | `error_not_found` |
| `permission_denied` | 403 | 관리자 권한 없음 | "권한이 없습니다" | ❌ | `error_permission` |
| `db_connection_error` | 503 | 데이터베이스 연결 실패 | "데이터베이스 연결 오류" | ✅ | `error_db_connection` |
| `db_operation_error` | 500 | 데이터베이스 작업 오류 | "데이터베이스 작업 실패" | ✅ | `error_db_operation` |
| `network_error` | 0 | 네트워크 오류 | "네트워크 오류가 발생했습니다" | ✅ | `error_network` |
| `timeout` | 408 | 요청 타임아웃 | "요청이 시간 초과되었습니다" | ✅ | `error_timeout` |
| `unknown_error` | 500 | 예기치 않은 오류 | "알 수 없는 오류가 발생했습니다" | ✅ | `error_unknown` |

---

## 5. 성능 및 제약

### 성공 기준 (SC) 매핑

| 성공 기준 | 데이터 모델 포인트 | 측정 방법 |
|---------|:--|:--|
| SC-003: 삭제 < 2초 | `QADeleteResult.timestamp` - `QADeleteRequest.timestamp` | Langfuse span duration |
| SC-004: 정확성 100% | `QADeleteResult.success` + `qa_id` 일치 | 통합 테스트 |
| SC-005: 오류 명확성 | `QADeleteResult.message` (사용자 친화적) | UI 검증 |
| SC-006: 감사 추적 100% | `QADeleteRequest.admin_user` + 타임스탐프 | Langfuse 기록 확인 |

---

## 6. 다음 단계

### Phase 1 계속
- ✅ data-model.md (이 파일)
- ⏳ contracts/delete-request.md (API 종류)
- ⏳ contracts/delete-response.md (API 응답 구조)
- ⏳ quickstart.md (통합 가이드)

### Phase 2  
- 테스트 케이스 작성 (모델 검증, 상태 전이)
- Langfuse 계측 포인트 구현
- 엣지 케이스 테스트
