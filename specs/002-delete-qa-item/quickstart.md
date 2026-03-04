# Quickstart: Q&A 삭제 기능 검증

## 1. 환경 준비
- 작업 브랜치: `002-delete-qa-item`
- Python 가상환경 활성화 (Windows PowerShell):
  - `& C:/fun/qa-chat/.venv/Scripts/Activate.ps1`
- 의존성 설치:
  - `pip install -r requirements.txt`

## 2. 테스트 우선 검증
- 단위 테스트:
  - `python -m pytest tests/unit/test_qa_delete_service.py -v`
  - `python -m pytest tests/unit/test_admin_list_tab.py -v`
- 통합/계약 테스트:
  - `python -m pytest tests/integration/test_admin_delete_flow.py -v`
  - `python -m pytest tests/contract/test_chromadb_delete.py -v`

## 3. 수동 실행
- 앱 실행:
  - `python src/main.py`
- 관리자 로그인(기본 비밀번호 1234)
- 관리자 > 목록 조회 탭 진입
- 각 카드 우측 `🗑️` 버튼 노출 확인

## 4. 삭제 플로우 확인
1. `🗑️` 클릭 → 확인 다이얼로그 노출
2. `아니오` 클릭 → 닫힘/미삭제 확인
3. 다시 `🗑️` 클릭 후 `예` → 삭제 수행
4. 토스트 메시지 확인:
   - 진행: `삭제 중...`
   - 성공: `✓ 삭제되었습니다`
   - 실패: `❌ 삭제 실패했습니다 - [원인]`
5. 목록 자동 갱신 및 대상 항목 제거 확인

## 5. Edge Case 확인
- 같은 항목을 두 번 연속 삭제 시 두 번째 요청은 not-found 오류
- 페이지 마지막 항목 삭제 시 페이지 리셋 동작 확인
- 빠른 연타 클릭 시 중복 삭제 방지 확인
