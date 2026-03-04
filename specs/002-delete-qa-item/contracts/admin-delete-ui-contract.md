# Contract: Admin Delete UI Flow

## Components
- 카드 헤더 우측 삭제 버튼: `🗑️`
- 확인 다이얼로그 문구: `이 항목을 삭제하시겠습니까?`
- 다이얼로그 액션: `예`, `아니오`
- 상태 메시지: 상단 토스트(`gr.Info`, `gr.Error`)

## Event Flow
1. 삭제 버튼 클릭
   - 입력: `qa_id`
   - 출력: `show_dialog=True`, `selected_qa_id=<id>`
2. "아니오" 클릭 또는 외부 클릭
   - 출력: `show_dialog=False`, 삭제 미수행
3. "예" 클릭
   - 출력(즉시): `is_deleting=True`, `gr.Info("삭제 중...")`
   - 백엔드: `QADeleteService.delete_qa_item(...)`
4. 성공 시
   - 출력: `gr.Info("✓ 삭제되었습니다")`
   - 후속: 목록 새로고침, 필요 시 페이지=1 리셋
5. 실패 시
   - 출력: `gr.Error("❌ 삭제 실패했습니다 - [원인]")`
   - 상태: 재시도 가능 상태로 복귀

## UI Rules
- 항목이 없으면 삭제 버튼 렌더링하지 않음
- `is_deleting=True` 동안 확인 버튼 중복 클릭 방지
- 접근성: 버튼 텍스트/타이틀로 의미 전달
