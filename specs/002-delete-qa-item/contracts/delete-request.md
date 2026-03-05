# API 계약: 삭제 요청

**기능**: Q&A 항목 삭제 기능 | **계약**: 삭제 작업 요청 | **날짜**: 2026-03-05

## 개요

이 문서는 Q&A 항목 삭제 요청이 어떻게 구성되고 처리되는지 정의합니다. 이것은 **벡터 인식 데이터 계약** (헌법 원칙 II)의 일부입니다.

---

## 요청 구조

### 엔드포인트 (개념적)

```
Service: QADeleteService
Method: delete_qa_item(request: QADeleteRequest) -> QADeleteResult
```

### 요청 설정

```python
class QADeleteRequest:
    """
    Q&A 삭제 요청의 완전한 정의
    """
    
    # 필드
    qa_id: str              # 삭제할 항목의 고유 ID
    admin_user: str         # 삭제 요청 관리자
    timestamp: datetime     # 요청 시각 (UTC)
    
    # 입력 근원
    # - Gradio UI: hidden_qa_id textbox → open_delete_dialog()
    # - 데이터 모델: data-model.md QADeleteRequest 참조
```

---

## 필드 명세

### 필드 1: `qa_id` (string)

**설명**: 삭제 대상 Q&A의 고유 해시 ID

**형식**: 
- 영문/숫자/하이픈 조합  
- 길이: 8-64자

**예시**:
```
"abc123def456"
"ca7b8e9f-hash-id"
```

**원본**: `QAItem.get_hash_key()`로 생성 (질문 텍스트 기반 해시)

**검증**:
```python
# 필수 검증
if not qa_id or not qa_id.strip():
    raise ValueError("qa_id는 비워둘 수 없습니다")

# 형식 검증 (정규식)
if not re.match(r'^[a-zA-Z0-9-]+$', qa_id):
    raise ValueError("qa_id 형식이 올바르지 않습니다")
```

**계약 보장**: 
- ✅ 이 ID는 ChromaDB 컬렉션에 존재하는 문서 ID와 정확히 일치
- ✅ 삭제 후 같은 ID로 재조회하면 404 응답
- ✅ 대소문자 구분함

---

### 필드 2: `admin_user` (string)

**설명**: 삭제를 요청한 관리자 사용자명

**형식**:
- 영문/숫자/언더스코어 조합
- 길이: 1-50자
- 예: `"admin"`, `"manager_001"`

**검증**:
```python
if not admin_user or not admin_user.strip():
    raise ValueError("admin_user는 비워둘 수 없습니다")

if len(admin_user) > 50:
    raise ValueError("admin_user는 50자 이하여야 합니다")
```

**용도**:
- 감사 추적 (누가 삭제했는가)
- Langfuse 기록
- 향후 권한 검증 확장 가능

---

### 필드 3: `timestamp` (datetime)

**설명**: 요청 생성 시각 (UTC)

**형식**: ISO 8601 UTC  
예: `"2026-03-05T19:00:00Z"`

**자동 설정**: 요청 생성 시 자동으로 현재 UTC 시각 할당

**검증**:
```python
# 미래 시각은 거부 (클라이언트 시계 오류 방지)
if timestamp > datetime.utcnow() + timedelta(seconds=60):
    raise ValueError("미래 시각 요청은 거부합니다")

# 너무 과거는 거부 (데이터 정합성)
if timestamp < datetime.utcnow() - timedelta(days=7):
    raise ValueError("7일 이상 과거의 요청은 거부합니다")
```

---

## 요청 흐름

### 1. Gradio UI에서 발생

```python
# admin_list_tab.py의 render_qa_cards()
onclick="deleteQA('{item.id}')"  # ← JavaScript deleteQA 함수 호출

# JavaScript에서
window.deleteQA = function(qaId) {
    hiddenInput.value = qaId;  # ← hidden_qa_id에 ID 저장
    triggerBtn.click();        # ← hidden_delete_trigger 버튼 클릭 (백엔드 연결)
}
```

### 2. Gradio 백엔드에서 처리

```python
# admin_list_tab.py의 open_delete_dialog()
def open_delete_dialog(qa_id: str, state: Dict[str, Any]):
    # qa_id 검증
    if not qa_id or not qa_id.strip():
        raise gr.Error("삭제할 항목을 선택해주세요")
    
    # 상태 업데이트 (UI 다이얼로그 열기)
    return gr.update(visible=True), ...
```

### 3. 사용자 확인 후

```python
# admin_list_tab.py의 confirm_delete()
def confirm_delete(state: Dict[str, Any], page: int):
    selected_qa_id = state.get("selected_qa_id")
    
    # QADeleteRequest 생성
    request = QADeleteRequest(
        qa_id=selected_qa_id,
        admin_user="admin",  # ← 현재는 고정값, 향후 session에서 가져올 수 있음
    )
    
    # QADeleteService에 전달
    result = delete_service.delete_qa_item(request)
```

---

## 예제

### 정상 요청

```json
{
  "qa_id": "abc123def456",
  "admin_user": "admin",
  "timestamp": "2026-03-05T19:00:00Z"
}
```

### 오류 요청

```json
{
  "qa_id": "",
  "admin_user": "admin"
}
```
❌ **오류**: qa_id 비어있음 → ValueError 발생 → "qa_id는 비워둘 수 없습니다"

---

## 처리 보장

| 보장 | 설명 |
|------|------|
| **원자성** | qa_id가 존재하면 삭제 실행, 없으면 "not_found" 오류 (중간 상태 없음) |
| **멱등성** (부분) | 같은 요청을 2번 보내도 오류는 같음 (첫 번째 성공, 두 번째 "not_found") |
| **추적 가능성** | admin_user + timestamp로 누가 언제 요청했는지 기록 |
| **감사 로그** | Langfuse span으로 모든 삭제 시도 기록 |

---

## 제약사항

### 알려진 제약

1. **관리자만 가능**: 인증 없는 요청은 처리 불가
2. **동시성**: 같은 항목을 2개 관리자가 동시에 삭제 시 먼저 온 것만 성공
3. **pH7 연속성**: 한 번 삭제된 항목은 복구 불가 (out of scope)
4. **타임아웃**: 30초 이상 응답 없으면 네트워크 오류로 간주

---

## 다음 단계

- ✅ contracts/delete-request.md (이 파일)
- ⏳ contracts/delete-response.md (응답 명세)
- [data-model.md](../data-model.md) 참조
- [plan.md](../plan.md) 참조
