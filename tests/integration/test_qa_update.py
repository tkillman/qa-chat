"""
통합 테스트: Q&A 관리 UI (Gradio + 서비스)
Spec US3: 관리자가 Q&A를 추가/수정하고 ChromaDB를 업데이트
Spec FR-008: 중복 질문은 기존 항목 덮어쓰기
Spec FR-010: 관리자 입력 제한 (질문 500자, 답변 2000자)
"""
import pytest
import os
from src.main import QAChatApp
from src.config import INIT_FILE_PATH, MAX_ADMIN_QUESTION_LENGTH, MAX_ADMIN_ANSWER_LENGTH


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """각 테스트 전후로 파일 정리"""
    # 테스트 전: 기존 파일 정리
    if os.path.exists(INIT_FILE_PATH):
        os.remove(INIT_FILE_PATH)
    
    yield
    
    # 테스트 후: 정리
    if os.path.exists(INIT_FILE_PATH):
        os.remove(INIT_FILE_PATH)


@pytest.fixture
def app():
    """QA Chat 앱 인스턴스"""
    qa_app = QAChatApp()
    qa_app.admin_logged_in = True  # 로그인 상태로 설정
    return qa_app


class TestQAUpdateIntegration:
    """Q&A 업데이트 통합 테스트 (UI + 서비스)"""
    
    def test_update_qa_requires_login(self):
        """목표: 로그인 없이 Q&A 업데이트 불가"""
        app = QAChatApp()
        app.admin_logged_in = False  # 미로그인 상태
        
        msg = app.update_qa("Question", "Answer")
        assert "로그인" in msg or "인증" in msg
    
    def test_add_new_qa_via_ui(self, app):
        """목표: UI를 통해 새 Q&A 항목 추가"""
        msg = app.update_qa("How to install?", "Run pip install package")
        
        assert "추가" in msg or "저장" in msg
        assert "✓" in msg
    
    def test_update_existing_qa_via_ui(self, app):
        """목표: UI를 통해 기존 Q&A 항목 업데이트"""
        # 첫 번째 추가
        app.update_qa("What is AI?", "Artificial Intelligence")
        
        # 같은 질문으로 업데이트
        msg = app.update_qa("What is AI?", "Advanced Intelligent System")
        
        assert "수정" in msg or "업데이트" in msg
        assert "✓" in msg
    
    def test_ui_validates_input_length_question(self, app):
        """목표: UI에서 질문 길이 검증"""
        long_question = "Q" * (MAX_ADMIN_QUESTION_LENGTH + 1)
        
        msg = app.update_qa(long_question, "Answer")
        assert "500자" in msg or "글자" in msg
    
    def test_ui_validates_input_length_answer(self, app):
        """목표: UI에서 답변 길이 검증"""
        long_answer = "A" * (MAX_ADMIN_ANSWER_LENGTH + 1)
        
        msg = app.update_qa("Question", long_answer)
        assert "2000자" in msg or "글자" in msg
    
    def test_duplicate_handling_in_ui(self, app):
        """목표: UI에서 중복 질문 처리 (FR-008)"""
        # 첫 번째 Q&A 추가
        app.update_qa("Is Python easy?", "Yes, very easy")
        
        # 대소문자 다르게 같은 질문으로 업데이트
        msg = app.update_qa("is python easy?", "Yes, but needs practice")
        
        # 수정되어야 함
        assert "수정" in msg or "업데이트" in msg
        assert "✓" in msg
    
    def test_error_handling_in_ui(self, app):
        """목표: UI에서 오류 처리"""
        # 빈 질문
        msg = app.update_qa("", "Answer")
        assert "입력" in msg or "질문" in msg
        
        # 빈 답변
        msg = app.update_qa("Question", "")
        assert "입력" in msg or "답변" in msg
    
    def test_malformed_input_handling(self, app):
        """목표: 잘못된 입력 처리"""
        # 공백만 있는 입력
        msg = app.update_qa("   ", "Answer")
        assert "입력" in msg or "질문" in msg
        
        msg = app.update_qa("Question", "   ")
        assert "입력" in msg or "답변" in msg
    
    def test_special_characters_in_qa(self, app):
        """목표: 특수문자 포함 Q&A 처리"""
        msg = app.update_qa(
            "What's the difference between @ & #?",
            "@ is for mention, # is for hashtag!"
        )
        
        assert "✓" in msg
    
    def test_unicode_in_qa(self, app):
        """목표: 유니코드 포함 Q&A 처리 (한글 등)"""
        msg = app.update_qa(
            "Python이란 무엇인가요? 🐍",
            "Python은 프로그래밍 언어입니다!"
        )
        
        assert "✓" in msg
    
    def test_qa_persistence_across_calls(self, app):
        """목표: 추가된 Q&A가 파일에 저장되고 유지됨"""
        # 첫 번째 Q&A 추가
        msg1 = app.update_qa("Q1", "A1")
        assert "✓" in msg1
        
        # 두 번째 Q&A 추가
        msg2 = app.update_qa("Q2", "A2")
        assert "✓" in msg2
        
        # 같은 질문으로 업데이트
        msg3 = app.update_qa("Q1", "A1-Updated")
        assert "수정" in msg3 or "업데이트" in msg3
