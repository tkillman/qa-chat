# Contract: Admin UI and Callback Interface

## Scope
Gradio 기반 관리자 인증/관리 패널의 콜백 입력·출력 계약을 정의한다.

## Callback 1: `admin_login(password)`
- Inputs:
  - `password: str`
- Outputs (ordered, fixed length = 6):
  1. `login_status` (`gr.Markdown` update)
  2. `admin_header` (`gr.Markdown` visibility update)
  3. `question_input` (`gr.Textbox` visibility update)
  4. `answer_input` (`gr.Textbox` visibility update)
  5. `add_btn` (`gr.Button` visibility update)
  6. `add_status` (`gr.Textbox` visibility update)
- Rules:
  - Gradio layout 컴포넌트(`Group/Row/Column/Tab`)는 outputs로 사용하지 않는다.
  - 성공 시 관리자 관련 출력은 모두 `visible=True`.
  - 실패/빈 비밀번호 시 관리자 관련 출력은 모두 `visible=False`.
  - 상태 메시지는 항상 `login_status`에 표시된다.

## Callback 2: `update_qa(question, answer)`
- Inputs:
  - `question: str` (1..500)
  - `answer: str` (1..2000)
- Outputs:
  - `add_status` (`gr.Textbox` value)
- Rules:
  - 전역 인증 상태가 `False`면 업데이트 거부 메시지 반환.
  - 동일 question은 덮어쓰기 처리.

## Callback 3: `search_answer(question)`
- Inputs:
  - `question: str` (1..500)
- Outputs:
  1. `answer_output: str`
  2. `similarity_output: float`
- Rules:
  - top-k=1 결과만 반환.
  - 유사도 임계값 0.7 미만이면 미검색 처리.
  - 미검색 시 answer는 정확히 `답변을 찾을 수 없습니다`, similarity=0.0.

## Admin Logout Contract
- UI는 로그아웃 버튼을 제공해야 한다.
- 로그아웃 시 전역 인증 상태는 즉시 `False`.
- 로그아웃 직후 관리자 입력 컴포넌트는 `visible=False`로 전환.

## Error/Observability Contract
- 로그인 성공/실패, 검색 실패, 업데이트 실패는 Langfuse 로깅 대상이다.
- 콜백 예외는 사용자 메시지 + 로깅으로 처리한다.

## Implementation Checklist
- [x] `admin_login` outputs는 값 컴포넌트 업데이트만 사용 (layout output 금지)
- [x] 로그인 성공 시 관리자 입력 컴포넌트 `visible=True`
- [x] 로그인 실패/빈 비밀번호 시 관리자 입력 컴포넌트 `visible=False`
- [x] 로그아웃 버튼 제공 및 전역 인증 상태 해제
