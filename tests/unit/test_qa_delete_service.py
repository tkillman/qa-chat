"""
Q&A 삭제 서비스 단위 테스트
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock

from src.models.qa_delete_models import QADeleteRequest, QADeleteResult
from src.services.qa_delete_service import QADeleteService


@pytest.fixture
def qa_delete_service():
    """테스트용 QADeleteService 인스턴스"""
    # 싱글톤 초기화 상태 리셋
    QADeleteService._instance = None
    service = QADeleteService()
    return service


@pytest.fixture
def valid_delete_request():
    """유효한 삭제 요청"""
    return QADeleteRequest(
        qa_id="hash_abc123",
        admin_user="admin01",
        timestamp=datetime(2024, 1, 15, 10, 30, 0)
    )


class TestQADeleteRequest:
    """QADeleteRequest 데이터 모델 테스트"""
    
    def test_create_delete_request_with_defaults(self):
        """기본값으로 삭제 요청 생성"""
        request = QADeleteRequest(
            qa_id="hash_test",
            admin_user="admin"
        )
        assert request.qa_id == "hash_test"
        assert request.admin_user == "admin"
        assert isinstance(request.timestamp, datetime)
    
    def test_create_delete_request_with_custom_timestamp(self):
        """커스텀 타임스탬프로 요청 생성"""
        timestamp = datetime(2024, 1, 15, 10, 0, 0)
        request = QADeleteRequest(
            qa_id="hash_test",
            admin_user="admin",
            timestamp=timestamp
        )
        assert request.timestamp == timestamp


class TestQADeleteResult:
    """QADeleteResult 데이터 모델 테스트"""
    
    def test_successful_result(self):
        """성공 결과 생성"""
        result = QADeleteResult(
            success=True,
            qa_id="hash_abc123",
            message="삭제 성공"
        )
        assert result.success is True
        assert result.qa_id == "hash_abc123"
        assert result.error_reason is None
    
    def test_failed_result_requires_error_reason(self):
        """실패 결과는 error_reason 필수"""
        with pytest.raises(ValueError, match="error_reason이 필수"):
            QADeleteResult(
                success=False,
                qa_id="hash_abc123",
                message="삭제 실패"
            )
    
    def test_failed_result_with_error_reason(self):
        """오류 이유와 함께 실패 결과 생성"""
        result = QADeleteResult(
            success=False,
            qa_id="hash_abc123",
            message="삭제 실패",
            error_reason="not_found"
        )
        assert result.success is False
        assert result.error_reason == "not_found"
    
    def test_empty_qa_id_raises_error(self):
        """빈 qa_id는 오류 발생"""
        with pytest.raises(ValueError, match="qa_id는 빈 값"):
            QADeleteResult(
                success=True,
                qa_id="",
                message="메시지"
            )
    
    def test_empty_message_raises_error(self):
        """빈 메시지는 오류 발생"""
        with pytest.raises(ValueError, match="message는 빈 값"):
            QADeleteResult(
                success=True,
                qa_id="hash_test",
                message=""
            )


class TestQADeleteService:
    """QADeleteService 테스트"""
    
    def test_singleton_pattern(self):
        """싱글톤 패턴 검증"""
        QADeleteService._instance = None
        service1 = QADeleteService()
        service2 = QADeleteService()
        assert service1 is service2
    
    def test_service_initialization(self, qa_delete_service):
        """서비스 초기화"""
        assert qa_delete_service is not None
        assert qa_delete_service._initialized is True
    
    def test_delete_qa_item_success(self, qa_delete_service, valid_delete_request):
        """Q&A 항목 삭제 성공"""
        # Mock 설정
        mock_chromadb_instance = Mock()
        mock_langfuse_instance = Mock()
        mock_langfuse_instance.get_client.return_value = None  # Langfuse 비활성화
        
        qa_delete_service.chromadb_service = mock_chromadb_instance
        qa_delete_service.langfuse_service = mock_langfuse_instance
        
        # 삭제 실행
        result = qa_delete_service.delete_qa_item(valid_delete_request)
        
        # 검증
        assert result.success is True
        assert result.qa_id == "hash_abc123"
        assert "삭제" in result.message
        mock_chromadb_instance.delete.assert_called_once_with("hash_abc123")
    
    def test_delete_qa_item_missing_admin_user(self, qa_delete_service):
        """admin_user 없이 삭제 요청"""
        request = QADeleteRequest(
            qa_id="hash_test",
            admin_user=""
        )
        
        qa_delete_service.chromadb_service = Mock()
        qa_delete_service.langfuse_service = Mock()
        qa_delete_service.langfuse_service.get_client.return_value = None
        
        result = qa_delete_service.delete_qa_item(request)
        
        assert result.success is False
        assert result.error_reason == "unknown_error"
    
    def test_delete_qa_item_not_found(self, qa_delete_service, valid_delete_request):
        """존재하지 않는 항목 삭제"""
        mock_chromadb_instance = Mock()
        mock_chromadb_instance.delete.side_effect = KeyError("항목을 찾을 수 없음")
        
        mock_langfuse_instance = Mock()
        mock_langfuse_instance.get_client.return_value = None  # Langfuse 비활성화
        
        qa_delete_service.chromadb_service = mock_chromadb_instance
        qa_delete_service.langfuse_service = mock_langfuse_instance
        
        result = qa_delete_service.delete_qa_item(valid_delete_request)
        
        assert result.success is False
        assert result.error_reason == "not_found"
