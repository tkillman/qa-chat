# Data Model: Q&A 항목 삭제 기능

## 1) QADeleteRequest

삭제 요청 입력 모델.

### Fields
- `qa_id: str` (required)
  - 의미: 삭제 대상 Q&A의 해시 ID
  - 규칙: 빈 문자열 불가
- `admin_user: str` (required)
  - 의미: 삭제를 수행한 관리자 식별자
  - 규칙: 빈 문자열 불가
- `timestamp: datetime` (required, default=now)
  - 의미: 삭제 요청 시각

### Validation Rules
- `qa_id`가 비어 있으면 요청 거부
- `admin_user`가 비어 있으면 요청 거부

## 2) QADeleteResult

삭제 처리 결과 출력 모델.

### Fields
- `success: bool` (required)
- `qa_id: str` (required)
- `message: str` (required)
- `error_reason: Optional[str]`

### Validation Rules
- `qa_id`/`message` 빈 값 불가
- `success=False`이면 `error_reason` 필수

## 3) UI DeletionState (Gradio State)

삭제 다이얼로그 제어용 상태 모델.

### Fields
- `show_dialog: bool`
- `selected_qa_id: Optional[str]`
- `selected_question_preview: Optional[str]`
- `is_deleting: bool`

### State Transitions
1. `idle`: `show_dialog=False, selected_qa_id=None, is_deleting=False`
2. `confirm_open`: 삭제 버튼 클릭 → `show_dialog=True`, 대상 ID 설정
3. `deleting`: 확인("예") 클릭 → `is_deleting=True`, 버튼 비활성화
4. `done_success`: 삭제 성공 → 목록 갱신 + 토스트 + `idle` 복귀
5. `done_error`: 삭제 실패 → 오류 토스트 + `confirm_open` 또는 `idle` 복귀
6. `cancelled`: "아니오" 또는 외부 클릭 → `idle` 복귀

## 4) Relationship
- UI(`DeletionState`)가 `QADeleteRequest`를 생성해 서비스 호출
- 서비스가 `QADeleteResult` 반환
- 결과에 따라 UI 상태/토스트/목록 리프레시 분기

## 5) Edge Case Mapping
- 동시 삭제(EC-002): 두 번째 요청은 `success=False`, `error_reason="항목을 찾을 수 없습니다"`
- 마지막 항목 삭제(EC-006): 현재 페이지 무효 시 페이지를 1로 리셋
- 중복 클릭(EC-007): `is_deleting=True` 동안 확인 버튼 비활성화
