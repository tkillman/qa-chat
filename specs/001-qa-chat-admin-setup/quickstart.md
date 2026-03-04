# Quickstart: QA Chat 관리자 및 초기 설정

## 목적
이 가이드는 스펙 `001-qa-chat-admin-setup`의 핵심 흐름(초기 로드, 관리자 로그인/로그아웃, Q&A 업데이트, 사용자 검색)을 로컬에서 빠르게 검증한다.

## 1. 환경 준비
```bash
# 프로젝트 루트
cd C:/fun/qa-chat

# 가상환경 활성화 (PowerShell)
.venv/Scripts/Activate.ps1

# 의존성 설치
pip install -r requirements.txt
```

## 2. 필수 설정
```bash
# .env (없으면 기본 1234 사용)
ADMIN_PASSWORD=1234
SIMILARITY_THRESHOLD=0.7
```

`data/init.txt`는 JSONL 형식이어야 한다.
```json
{"question":"Python이란?","answer":"프로그래밍 언어입니다"}
{"question":"Docker란?","answer":"컨테이너 플랫폼입니다"}
```

## 3. 앱 실행
```bash
python src/main.py
```
브라우저에서 `http://127.0.0.1:7860` 접속.

## 4. 시나리오 검증

### A) 초기 로딩
- 앱 시작 로그에서 초기 로드 성공/실패 메시지 확인.
- `init.txt`가 없거나 일부 줄이 손상되어도 앱은 기동되어야 하며 손상 줄은 무시된다.

### B) 관리자 로그인/로그아웃
- 관리자 탭에서 `1234` 로그인 성공 시 관리자 입력 영역이 표시된다.
- 잘못된 비밀번호 입력 시 상태 메시지 표시, 관리자 영역은 숨김 유지.
- 로그아웃 버튼 클릭 시 전역 로그인 상태 해제 및 로그인 화면 복귀.

### C) Q&A 업데이트
- 관리자 로그인 상태에서 질문/답변 입력 후 업데이트 버튼 클릭.
- 같은 질문 재입력 시 기존 항목이 덮어쓰기 되어야 한다.
- 업데이트 후 `data/init.txt`와 ChromaDB 검색 결과가 동일한 최신 값을 반환해야 한다.

### D) 사용자 검색
- 사용자 탭에서 질문 입력 시 유사도 임계값(0.7) 이상 1건만 반환.
- 결과 없음 시 정확히 `답변을 찾을 수 없습니다` 반환.

## 5. 테스트 실행 (권장 순서)
```bash
# 빠른 회귀
pytest tests/integration/test_admin_login.py -q
pytest tests/integration/test_initial_load.py -q
pytest tests/integration/test_qa_update.py -q

# 전체 테스트
pytest -q
```

## 6. 완료 기준
- 관리자 로그인/로그아웃이 명세대로 동작한다.
- 검색 결과 없음 문구가 고정 문자열과 정확히 일치한다.
- 중복 질문 업데이트가 덮어쓰기로 처리된다.
- Langfuse 추적이 로그인/검색/업데이트/오류 이벤트에 남는다.

## 7. 회귀 실행 결과 (T039)
- 실행 명령: `python -m pytest -q`
- 실행 일시: 2026-03-04
- 결과: `139 passed`
- Triaging 메모:
  - 기능 실패 없음
  - `datetime.utcnow()` 관련 deprecation warning 다수 존재 (`src/utils/cache.py`, `src/models/cache_models.py`)
  - 본 구현 범위 외 경고로 분리 추적 권장
