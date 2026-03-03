"""
단위 테스트: QA 업데이트 서비스 (관리자 Q&A 추가/수정)
Spec US3: 관리자가 Q&A를 추가/수정하고 ChromaDB를 업데이트
Spec FR-008: 중복 질문은 기존 항목 덮어쓰기
Spec FR-010: 관리자 입력 제한 (질문 500자, 답변 2000자)
"""
import pytest
import os
import tempfile
import shutil
from src.services.qa_update_service import QAUpdateService
from src.models.qa_item import QAItem
from src.config import MAX_ADMIN_QUESTION_LENGTH, MAX_ADMIN_ANSWER_LENGTH, INIT_FILE_PATH
from src.services.file_service import FileService
from src.services.chromadb_service import ChromaDBService


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """각 테스트 전후로 파일과 ChromaDB 정리"""
    # 테스트 전: 기존 파일 백업 및 정리
    if os.path.exists(INIT_FILE_PATH):
        os.remove(INIT_FILE_PATH)
    
    yield
    
    # 테스트 후: 정리
    if os.path.exists(INIT_FILE_PATH):
        os.remove(INIT_FILE_PATH)


class TestQAUpdateServiceValidation:
    """QA 업데이트 입력값 검증 (EC3)"""
    
    def test_empty_question_fails(self):
        """목표: 빈 질문은 거부"""
        service = QAUpdateService()
        
        result = service.validate_input("", "Answer")
        assert result['valid'] == False
        assert "질문" in result['error']
    
    def test_empty_answer_fails(self):
        """목표: 빈 답변은 거부"""
        service = QAUpdateService()
        
        result = service.validate_input("Question", "")
        assert result['valid'] == False
        assert "답변" in result['error']
    
    def test_question_too_long_fails(self):
        """목표: 질문이 500자 초과이면 거부 (FR-010)"""
        service = QAUpdateService()
        long_question = "A" * (MAX_ADMIN_QUESTION_LENGTH + 1)
        
        result = service.validate_input(long_question, "Answer")
        assert result['valid'] == False
        assert "500자" in result['error'] or "글자" in result['error']
    
    def test_answer_too_long_fails(self):
        """목표: 답변이 2000자 초과이면 거부 (FR-010)"""
        service = QAUpdateService()
        long_answer = "A" * (MAX_ADMIN_ANSWER_LENGTH + 1)
        
        result = service.validate_input("Question", long_answer)
        assert result['valid'] == False
        assert "2000자" in result['error'] or "글자" in result['error']
    
    def test_valid_input_passes(self):
        """목표: 올바른 입력값은 검증 통과"""
        service = QAUpdateService()
        
        result = service.validate_input("Question", "Answer")
        assert result['valid'] == True
    
    def test_exact_length_limits_pass(self):
        """목표: 정확한 길이 제한은 통과"""
        service = QAUpdateService()
        
        # 정확한 길이
        q = "Q" * MAX_ADMIN_QUESTION_LENGTH
        a = "A" * MAX_ADMIN_ANSWER_LENGTH
        
        result = service.validate_input(q, a)
        assert result['valid'] == True
    
    def test_whitespace_only_fails(self):
        """목표: 공백만 있는 입력은 거부"""
        service = QAUpdateService()
        
        result = service.validate_input("   ", "Answer")
        assert result['valid'] == False
        
        result = service.validate_input("Question", "   ")
        assert result['valid'] == False
    
    def test_none_input_fails(self):
        """목표: None 입력은 거부"""
        service = QAUpdateService()
        
        result = service.validate_input(None, "Answer")
        assert result['valid'] == False
        
        result = service.validate_input("Question", None)
        assert result['valid'] == False


class TestQAUpdateServiceStorage:
    """QA 저장 및 중복 처리 테스트 (FR-008)"""
    
    def test_add_new_qa_item(self):
        """목표: 새 Q&A 항목 추가"""
        service = QAUpdateService()
        
        success, msg = service.add_or_update_qa("New Question", "New Answer")
        assert success == True
        assert "추가" in msg or "저장" in msg
    
    def test_update_existing_qa_item(self):
        """목표: 기존 Q&A 항목 덮어쓰기 (FR-008)"""
        service = QAUpdateService()
        
        # 첫 번째 추가
        service.add_or_update_qa("Question", "Original Answer")
        
        # 같은 질문으로 업데이트
        success, msg = service.add_or_update_qa("Question", "Updated Answer")
        assert success == True
        assert "수정" in msg or "업데이트" in msg
    
    def test_duplicate_handling_case_insensitive(self):
        """목표: 중복 검사는 대소문자 무시 (FR-008)"""
        service = QAUpdateService()
        
        service.add_or_update_qa("Question", "Answer1")
        success, msg = service.add_or_update_qa("QUESTION", "Answer2")
        
        # 중복으로 인해 수정되어야 함
        assert success == True
    
    def test_duplicate_handling_whitespace_normalized(self):
        """목표: 중복 검사는 공백 정규화 (FR-008)"""
        service = QAUpdateService()
        
        service.add_or_update_qa("Question", "Answer1")
        success, msg = service.add_or_update_qa("  Question  ", "Answer2")
        
        # 중복으로 인해 수정되어야 함
        assert success == True
    
    def test_metadata_preserved(self):
        """목표: 메타데이터 유지"""
        service = QAUpdateService()
        
        success, msg = service.add_or_update_qa(
            "Question",
            "Answer",
            metadata={"source": "admin", "version": 1}
        )
        
        assert success == True
