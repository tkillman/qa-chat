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
        with gr.Blocks(title="QA Chat", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 📚 QA Chat")
            gr.Markdown("질문에 대한 답변을 제공하는 AI 챗봇")
            
            with gr.Tab("사용자"):
                gr.Markdown("## 질문하기")
                gr.Markdown("저장된 Q&A 중에서 유사한 답변을 찾아드립니다.")
                
                user_question = gr.Textbox(
                    label="질문",
                    placeholder="질문을 입력하세요...",
                    lines=2,
                )
                search_btn = gr.Button("답변 찾기", variant="primary")
                answer_output = gr.Textbox(
                    label="답변",
                    interactive=False,
                    lines=3,
                )
                similarity_output = gr.Number(
                    label="유사도",
                    interactive=False,
                )
                
                # 검색 버튼 클릭 시 동작 (US4에서 구현)
                search_btn.click(
                    fn=self.search_answer,
                    inputs=[user_question],
                    outputs=[answer_output, similarity_output]
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
                login_status = gr.Markdown("", visible=False)
                
                # 관리자 패널 (로그인 후 표시, US2에서 구현)
                with gr.Group(visible=False) as admin_panel:
                    gr.Markdown("## Q&A 관리")
                    
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
                    
                    # 추가/수정 버튼 클릭 시 동작 (US3에서 구현)
                    add_btn.click(
                        fn=self.update_qa,
                        inputs=[question_input, answer_input],
                        outputs=[add_status]
                    )
                
                # 로그인 버튼 클릭 시 동작 (US2에서 구현)
                login_btn.click(
                    fn=self.admin_login,
                    inputs=[password_input],
                    outputs=[login_status, admin_panel]
                )
        
        return interface
    
    def search_answer(self, question: str) -> tuple:
        """사용자 질문에 답변 검색 (US4)
        
        Spec:
        - 사용자 질문 입력 받기
        - ChromaDB에서 유사도 검색
        - 유사도 0.7 이상만 반환 (FR-004)
        - 최대 1개 결과만 반환 (FR-009)
        - Langfuse 로깅
        
        Args:
            question: 사용자 질문 (최대 1024자)
            
        Returns:
            (답변 텍스트, 유사도 점수) 또는 ("작답할 수 없습니다", 0.0)
        """
        try:
            # 입력값 검증
            if not question or not question.strip():
                msg = "질문을 입력해주세요"
                logger.warning("User search with empty question")
                return msg, 0.0
            
            # 사용자 검색 서비스 호출
            results = self.user_search_service.search_qa(question)
            
            if results and len(results) > 0:
                # 첫 번째 결과 반환 (최대 1개)
                result = results[0]
                answer = result.get('answer', '답변을 찾을 수 없습니다')
                similarity = result.get('similarity', 0.0)
                
                logger.info(f"User search successful: '{question[:50]}...' -> similarity: {similarity}")
                return answer, similarity
            else:
                # 결과 없음
                msg = "죄송합니다만, 해당 질문에 대한 답변을 찾지 못했습니다."
                logger.info(f"No results for user question: '{question[:50]}...'")
                return msg, 0.0
                
        except Exception as e:
            error_msg = "검색 중 오류가 발생했습니다."
            logger.error(f"Error searching answer: {e}")
            self.langfuse.log_error(
                error_type="user_search_ui_failed",
                error_message=str(e)
            )
            return error_msg, 0.0
    
    def admin_login(self, password: str) -> tuple:
        """관리자 로그인 (US2 - 패스워드 검증)
        
        Spec US2: 패스워드(1234) 검증 후 관리자 화면 진입
        Spec FR-002: 환경변수 ADMIN_PASSWORD (기본값: 1234)
        
        Args:
            password: 입력한 패스워드
            
        Returns:
            (상태 메시지, 관리자 패널 표시 여부)
        """
        if not password:
            # 빈 패스워드
            msg = "패스워드를 입력해주세요"
            self.langfuse.log_admin_login(success=False, reason="empty_password")
            return msg, False
        
        # 패스워드 검증
        is_valid = self.auth_service.verify_password(password)
        
        if is_valid:
            # 로그인 성공
            self.admin_logged_in = True
            msg = "✓ 로그인 성공하였습니다"
            self.langfuse.log_admin_login(success=True)
            logger.info("Admin login successful")
            return msg, True
        else:
            # 로그인 실패
            self.admin_logged_in = False
            msg = "✗ 패스워드가 틀렸습니다"
            self.langfuse.log_admin_login(success=False, reason="invalid_password")
            logger.warning("Admin login failed")
            return msg, False
    
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
        self.interface = self.create_interface()
        self.interface.queue(default_concurrency_limit=20)
        
        # 앱 선입 이벤트 등록 (on_startup은 Gradio 3.50+ 문법)
        logger.info("Launching Gradio interface...")
        self.interface.launch(share=share)


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
