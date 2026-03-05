"""
QA Chat 메인 애플리케이션 - Gradio UI
헌법 원칙: UI는 Gradio 사용, TDD, 관찰성
"""
import os
import sys

if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
import logging
from src.services.init_loader import get_init_loader
from src.services.auth_service import AuthService
from src.services.qa_update_service import get_qa_update_service
from src.services.user_search_service import get_user_search_service
from src.services.langfuse_service import get_langfuse_service
from src.ui.admin_list_tab import create_admin_list_tab
from src.config import LOG_LEVEL, MAX_USER_QUESTION_LENGTH, MAX_ADMIN_QUESTION_LENGTH, MAX_ADMIN_ANSWER_LENGTH

# 로깅 설정
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QAChatApp:
    """QA Chat 애플리케이션"""
    
    def __init__(self):
        """앱 초기화"""
        self.init_loader = get_init_loader()
        self.auth_service = AuthService()
        self.qa_update_service = get_qa_update_service()
        self.user_search_service = get_user_search_service()
        self.langfuse = get_langfuse_service()
        self.interface = None
        self.admin_logged_in = False

    def _set_admin_state(self, is_authenticated: bool) -> None:
        """전역 관리자 인증 상태 전이 규칙."""
        self.admin_logged_in = is_authenticated
    
    async def on_startup(self):
        """앱 시작 시 초기 로드 (US1)
        
        Spec US1: 앱 실행 시 init.txt의 데이터를 ChromaDB에 로드
        """
        logger.info("=== QA Chat Application Started ===")
        
        try:
            num_items, duration_ms, success = self.init_loader.load_initial_data()
            
            if success:
                logger.info(f"✓ Initial load successful: {num_items} items loaded in {duration_ms:.2f}ms")
            else:
                logger.warning(f"⚠ Initial load failed, starting with empty database")
            
        except Exception as e:
            logger.error(f"✗ Fatal error during startup: {e}")
            raise
    
    def create_interface(self) -> gr.Blocks:
        """Gradio 인터페이스 생성
        
        Returns:
            gr.Blocks 인터페이스
        """
        # CSS는 launch()에서 전달할 예정
        with gr.Blocks(title="QA Chat") as interface:
            # 카카오톡 스타일 CSS
            gr.HTML("""
            <style>
            .chat-container {
                background: #abc1d1;
                border-radius: 8px;
                padding: 20px;
                height: 600px;
                overflow-y: auto;
                margin-bottom: 20px;
            }
            .message-row {
                margin-bottom: 12px;
                display: flex;
                align-items: flex-end;
            }
            .message-row.user {
                justify-content: flex-end;
            }
            .message-row.bot {
                justify-content: flex-start;
            }
            .message-bubble {
                max-width: 60%;
                padding: 10px 14px;
                border-radius: 18px;
                word-wrap: break-word;
                font-size: 14px;
                line-height: 1.5;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            .message-bubble.user {
                background: #fee500;
                color: #000;
                border-bottom-right-radius: 4px;
            }
            .message-bubble.bot {
                background: #fff;
                color: #000;
                border-bottom-left-radius: 4px;
            }
            .message-time {
                font-size: 11px;
                color: #666;
                margin: 0 8px;
            }
            .empty-chat {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                color: #fff;
                opacity: 0.7;
            }
            .empty-chat-icon {
                font-size: 80px;
                margin-bottom: 20px;
            }
            </style>
            """)
            
            gr.Markdown("# 💬 QA Chat")
            gr.Markdown("질문에 대한 답변을 제공하는 AI 챗봇")
            
            with gr.Tab("사용자"):
                # 채팅 히스토리 상태 관리
                chat_history = gr.State([])
                
                # 채팅 화면
                chat_display = gr.HTML(
                    value=self._render_empty_chat(),
                    elem_classes="chat-container"
                )
                
                # 입력 영역
                with gr.Row():
                    user_question = gr.Textbox(
                        label="",
                        placeholder="메시지를 입력하세요...",
                        lines=1,
                        scale=9,
                        container=False,
                    )
                    search_btn = gr.Button("전송", variant="primary", scale=1)
                
                # 검색 버튼 클릭 시 동작
                search_btn.click(
                    fn=self.chat_interaction,
                    inputs=[user_question, chat_history],
                    outputs=[chat_display, chat_history, user_question]
                )
                
                # 엔터키로 전송
                user_question.submit(
                    fn=self.chat_interaction,
                    inputs=[user_question, chat_history],
                    outputs=[chat_display, chat_history, user_question]
                )
            
            with gr.Tab("관리자"):
                gr.Markdown("## 패스워드 입력")
                gr.Markdown("관리자 기능을 사용하려면 패스워드를 입력해주세요.")
                
                password_input = gr.Textbox(
                    label="패스워드",
                    type="password",
                    placeholder="패스워드 입력",
                )
                login_btn = gr.Button("로그인", variant="primary")
                logout_btn = gr.Button("로그아웃", variant="secondary")
                login_status = gr.Markdown("", visible=False)
                
                # 관리자 패널 (로그인 후 표시)
                with gr.Group(visible=False) as admin_panel:
                    admin_tabs = gr.Tabs()
                    with admin_tabs:
                        # Tab 1: Q&A 관리
                        with gr.Tab("✏️ Q&A 관리"):
                            gr.Markdown("### Q&A 항목 추가/수정")
                            
                            question_input = gr.Textbox(
                                label="질문",
                                placeholder="새로운 질문을 입력하세요",
                                lines=2,
                            )
                            answer_input = gr.Textbox(
                                label="답변",
                                placeholder="답변을 입력하세요",
                                lines=3,
                            )
                            add_btn = gr.Button("추가/수정", variant="primary")
                            add_status = gr.Textbox(
                                label="상태",
                                interactive=False,
                            )

                            # 추가/수정 버튼 클릭 시 동작
                            add_btn.click(
                                fn=self.update_qa,
                                inputs=[question_input, answer_input],
                                outputs=[add_status]
                            )
                        
                        # Tab 2: 목록 조회 (새로 추가)
                        list_tab = create_admin_list_tab()
                    
                    # 탭 선택 시 목록 탭이 선택되면 새로고침 트리거
                    if list_tab and len(list_tab) >= 6:
                        # hidden_refresh_trigger 값 변경으로 새로고침 트리거
                        admin_tabs.select(
                            fn=lambda: list_tab[5].update(value="refresh"),
                            outputs=[list_tab[5]]
                        )
                
                # 로그인 버튼 클릭 시 동작
                login_btn.click(
                    fn=self.admin_login,
                    inputs=[password_input],
                    outputs=[
                        login_status,
                        admin_panel,
                    ]
                )

                logout_btn.click(
                    fn=self.admin_logout,
                    inputs=[],
                    outputs=[
                        login_status,
                        admin_panel,
                    ]
                )
        
        return interface
    
    def _render_empty_chat(self) -> str:
        """빈 채팅 화면 렌더링"""
        return """
        <div class="chat-container">
            <div class="empty-chat">
                <div class="empty-chat-icon">💬</div>
                <div>질문을 입력하여 대화를 시작하세요</div>
            </div>
        </div>
        """
    
    def _render_chat_history(self, history: list) -> str:
        """채팅 히스토리를 카카오톡 스타일로 렌더링
        
        Args:
            history: [{"role": "user"|"bot", "message": str, "time": str}, ...]
            
        Returns:
            HTML 문자열
        """
        if not history:
            return self._render_empty_chat()
        
        messages_html = ""
        for msg in history:
            role = msg.get("role", "bot")
            message = msg.get("message", "")
            time = msg.get("time", "")
            
            # HTML 이스케이프
            message_escaped = (message
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('\n', '<br>'))
            
            if role == "user":
                messages_html += f"""
                <div class="message-row user">
                    <span class="message-time">{time}</span>
                    <div class="message-bubble user">{message_escaped}</div>
                </div>
                """
            else:
                messages_html += f"""
                <div class="message-row bot">
                    <div class="message-bubble bot">{message_escaped}</div>
                    <span class="message-time">{time}</span>
                </div>
                """
        
        return f"""
        <div class="chat-container">
            {messages_html}
        </div>
        """
    
    def chat_interaction(self, question: str, history: list):
        """카카오톡 스타일 채팅 인터랙션
        
        Args:
            question: 사용자 질문
            history: 채팅 히스토리
            
        Returns:
            (채팅 화면 HTML, 업데이트된 히스토리, 빈 입력창)
        """
        from datetime import datetime
        
        # 빈 질문 처리
        if not question or not question.strip():
            return self._render_chat_history(history), history, ""
        
        # 현재 시간
        current_time = datetime.now().strftime("%H:%M")
        
        # 사용자 메시지 추가
        history.append({
            "role": "user",
            "message": question,
            "time": current_time
        })
        
        # 임시로 사용자 메시지만 표시
        yield self._render_chat_history(history), history, ""
        
        try:
            # 길이 제한 검증
            if len(question) > MAX_USER_QUESTION_LENGTH:
                answer = f"질문은 {MAX_USER_QUESTION_LENGTH}자 이내여야 합니다"
            else:
                # 답변 검색
                results = self.user_search_service.search_qa(question)
                
                if results and len(results) > 0:
                    answer = results[0].get('answer', '답변을 찾을 수 없습니다')
                    logger.info(f"User search successful: '{question[:50]}...'")
                else:
                    answer = "죄송합니다. 관련된 답변을 찾을 수 없습니다. 😔"
                    logger.info(f"No results for user question: '{question[:50]}...'")
        
        except Exception as e:
            answer = "검색 중 오류가 발생했습니다."
            logger.error(f"Error searching answer: {e}")
            self.langfuse.log_error(
                error_type="user_search_ui_failed",
                error_message=str(e)
            )
        
        # 봇 응답 추가
        history.append({
            "role": "bot",
            "message": answer,
            "time": current_time
        })
        
        yield self._render_chat_history(history), history, ""
    
    def search_answer(self, question: str) -> tuple:
        """사용자 질문에 답변 검색 (US4)
        
        Spec:
        - 사용자 질문 입력 받기
        - ChromaDB에서 유사도 검색
        - 유사도 0.7 이상만 반환 (FR-004)
        - 최대 1개 결과만 반환 (FR-009)
        - Langfuse 로깅

        Args:
            question: 사용자 질문 (최대 500자)

        Returns:
            (답변 텍스트, 유사도 점수) 또는 ("답변을 찾을 수 없습니다", 0.0)
        """
        try:
            # 입력값 검증
            if not question or not question.strip():
                yield "질문을 입력해주세요"
                return
            
            # 길이 제한 검증 (FR-009)
            if len(question) > MAX_USER_QUESTION_LENGTH:
                yield f"질문은 {MAX_USER_QUESTION_LENGTH}자 이내여야 합니다"
                return

            # 사용자 검색 서비스 호출
            results = self.user_search_service.search_qa(question)
            
            if results and len(results) > 0:
                # 첫 번째 결과 반환 (최대 1개)
                result = results[0]
                answer = result.get('answer', '답변을 찾을 수 없습니다')
                
                logger.info(f"User search successful: '{question[:50]}...'")
                
                # 스트리밍: 한 글자씩 yield (마치 타이핑하듯)
                accumulated = ""
                for char in answer:
                    accumulated += char
                    yield accumulated
            else:
                # 결과 없음
                msg = "답변을 찾을 수 없습니다"
                logger.info(f"No results for user question: '{question[:50]}...'")
                yield msg
                
        except Exception as e:
            error_msg = "검색 중 오류가 발생했습니다."
            logger.error(f"Error searching answer: {e}")
            self.langfuse.log_error(
                error_type="user_search_ui_failed",
                error_message=str(e)
            )
            yield error_msg
    
    def admin_login(self, password: str) -> tuple:
        """관리자 로그인 (US2 - 패스워드 검증)
        
        Spec US2: 패스워드(1234) 검증 후 관리자 화면 진입
        Spec FR-002: 환경변수 ADMIN_PASSWORD (기본값: 1234)
        
        Args:
            password: 입력한 패스워드
            
        Returns:
            (로그인 상태 메시지, 관리자 패널 visible 상태)
        """
        if not password:
            # 빈 패스워드
            msg = "패스워드를 입력해주세요"
            self.langfuse.log_admin_login(success=False, reason="empty_password")
            return (
                gr.update(value=msg, visible=True),
                gr.update(visible=False),
            )
        
        # 패스워드 검증
        is_valid = self.auth_service.verify_password(password)
        
        if is_valid:
            # 로그인 성공
            self._set_admin_state(True)
            msg = "✓ 로그인 성공하였습니다"
            self.langfuse.log_admin_login(success=True)
            logger.info("Admin login successful")
            return (
                gr.update(value=msg, visible=True),
                gr.update(visible=True),
            )
        else:
            # 로그인 실패
            self._set_admin_state(False)
            msg = "✗ 패스워드가 틀렸습니다"
            self.langfuse.log_admin_login(success=False, reason="invalid_password")
            logger.warning("Admin login failed")
            return (
                gr.update(value=msg, visible=True),
                gr.update(visible=False),
            )

    def admin_logout(self) -> tuple:
        """관리자 로그아웃: 전역 인증 상태 해제 후 로그인 화면 복귀."""
        self._set_admin_state(False)
        self.langfuse.log_admin_logout(success=True)
        logger.info("Admin logout successful")

        return (
            gr.update(value="로그아웃되었습니다", visible=True),
            gr.update(visible=False),
        )
    
    def update_qa(self, question: str, answer: str) -> str:
        """Q&A 추가/수정 (US3)
        
        Spec:
        - 관리자 인증 필요 (로그인 상태 확인)
        - 입력값 검증 (길이 제한 FR-010)
        - 중복 질문 덮어쓰기 (FR-008)
        - Langfuse 추적
        
        Args:
            question: 질문 (최대 500자)
            answer: 답변 (최대 2000자)
            
        Returns:
            상태 메시지
        """
        # 로그인 상태 확인
        if not self.admin_logged_in:
            logger.warning("Q&A update attempted without admin login")
            return "✗ 관리자 로그인이 필요합니다"
        
        try:
            # QA 업데이트 서비스 호출
            success, msg = self.qa_update_service.add_or_update_qa(question, answer)
            
            # Langfuse에 UI 액션 로깅
            if success:
                logger.info(f"Q&A update success: {question[:50]}...")
            else:
                logger.warning(f"Q&A update failed: {msg}")
            
            return msg
            
        except Exception as e:
            error_msg = f"✗ Q&A 업데이트 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            self.langfuse.log_error(
                error_type="qa_update_ui_failed",
                error_message=str(e)
            )
            return error_msg
    
    def launch(self, share: bool = False):
        """앱 실행
        
        Args:
            share: Gradio 공유 링크 생성 여부
        """
        custom_css = """
        /* 탭 텍스트 크기 증가 */
        .tab-nav button {
            font-size: 18px !important;
            font-weight: 600 !important;
            padding: 12px 24px !important;
        }
        
        /* 탭 컨텐츠 패딩 */
        .tab-content-padding {
            padding: 24px !important;
        }
        
        /* 페이징 정보 중앙 정렬 */
        .page-info-center {
            text-align: center !important;
        }
        
        /* 페이지당 항목 수와 새로고침 버튼 우측 정렬, 10px 간격 */
        .control-row-right {
            display: flex !important;
            gap: 10px !important;
            justify-content: flex-end !important;
        }
        """
        
        self.interface = self.create_interface()
        self.interface.queue(default_concurrency_limit=20)
        
        # 앱 선입 이벤트 등록 (on_startup은 Gradio 3.50+ 문법)
        logger.info("Launching Gradio interface...")
        self.interface.launch(share=share, theme=gr.themes.Soft(), css=custom_css)


async def create_app():
    """앱 생성 및 초기화"""
    app = QAChatApp()
    await app.on_startup()
    return app


if __name__ == "__main__":
    import asyncio
    
    # 앱 초기화
    app = QAChatApp()
    
    # 비동기 초기화 수행
    asyncio.run(app.on_startup())
    
    # Gradio 앱 실행
    app.launch(share=False)
