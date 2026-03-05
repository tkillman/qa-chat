# Quickstart: Q&A 삭제 기능 검증

## 사전 준비

1. 프로젝트 루트 이동
2. 가상환경 활성화
3. 의존성 설치

```bash
cd c:/fun/qa-chat
pip install -r requirements.txt
```

## 앱 실행

```bash
python src/main.py
```

## 수동 검증 시나리오

1. 관리자 로그인
2. `📋 목록 조회` 탭 이동
3. 테이블 각 행의 `🗑️ 삭제` 버튼 확인
4. 삭제 버튼 클릭
5. 확인 다이얼로그(`이 항목을 삭제하시겠습니까?`) 확인
6. `아니오` 클릭 시 취소 확인
7. 다시 삭제 버튼 클릭 후 `예` 클릭
8. `삭제 중...` → `✓ 삭제되었습니다` 토스트 확인
9. 목록에서 해당 항목 제거 확인

## 엣지 케이스

- 동일 항목을 두 번 삭제 시 두 번째 요청은 `항목 없음` 오류
- 페이지 마지막 항목 삭제 후 페이지 1로 리셋되는지 확인
- 목록이 0건이 되면 빈 상태 메시지 표시 확인

## 테스트 실행

```bash
python -m pytest tests/unit/test_admin_list_tab.py tests/unit/test_qa_delete_service.py tests/integration/test_admin_delete_flow.py -q
```

## 기대 결과

- 확인 다이얼로그가 항상 선행 표시됨
- 삭제 성공/실패 토스트가 명확히 구분됨
- Langfuse에서 삭제 span 추적 가능
