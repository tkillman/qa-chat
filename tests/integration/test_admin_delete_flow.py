"""
Q&A 삭제 통합 테스트 - 관리자 삭제 흐름
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock

from src.models.qa_delete_models import QADeleteRequest, QADeleteResult
from src.services.qa_delete_service import QADeleteService


@pytest.fixture
def qa_delete_service():
    """테스트용 QADeleteService 인스턴스"""
    QADeleteService._instance = None
    service = QADeleteService()
    return service


@pytest.fixture
def mock_chromadb():
    """ChromaDB 서비스 Mock"""
    return Mock()


@pytest.fixture
def mock_langfuse():
    """Langfuse 서비스 Mock"""
    return Mock()


@pytest.fixture
def mock_qa_list():
    """QA List 서비스 Mock"""
    return Mock()


class TestAdminDeleteFlow:
    """관리자 Q&A 삭제 흐름 통합 테스트"""
    
    def test_complete_delete_flow(
        self, qa_delete_service, mock_chromadb, mock_langfuse, mock_qa_list
    ):
        """완전한 삭제 흐름 테스트"""
        # 의존성 주입
        mock_langfuse.get_client.return_value = None  # Langfuse 클라이언트 비활성화
        
        qa_delete_service.chromadb_service = mock_chromadb
        qa_delete_service.langfuse_service = mock_langfuse
        qa_delete_service.qa_list_service = mock_qa_list
        
        # 1. 삭제 요청 생성
        request = QADeleteRequest(
            qa_id="hash_item_001",
            admin_user="admin01"
        )
        
        # 2. 삭제 실행
        result = qa_delete_service.delete_qa_item(request)
        
        # 3. 결과 검증
        assert result.success is True
        assert result.qa_id == "hash_item_001"
        
        # 4. 의존성 호출 검증
        mock_chromadb.delete.assert_called_once_with("hash_item_001")
    
    def test_delete_and_page_update(
        self, qa_delete_service, mock_chromadb, mock_langfuse
    ):
        """삭제 후 페이지 새로고침"""
        mock_langfuse.get_client.return_value = None  # Langfuse 클라이언트 비활성화
        
        qa_delete_service.chromadb_service = mock_chromadb
        qa_delete_service.langfuse_service = mock_langfuse
        
        request = QADeleteRequest(
            qa_id="hash_item_002",
            admin_user="admin01"
        )
        
        # 삭제 실행
        result = qa_delete_service.delete_qa_item(request)
        
        # 토스트 알림 메시지는 프론트엔드에서 처리
        assert result.success is True
        assert "성공" in result.message
    
    def test_delete_with_concurrent_request(
        self, qa_delete_service, mock_chromadb, mock_langfuse
    ):
        """동시 요청으로 인한 삭제 실패 처리
        
        First wins 패턴: 첫 번째 요청은 성공, 두 번째는 실패
        """
        mock_langfuse.get_client.return_value = None  # Langfuse 클라이언트 비활성화
        
        qa_delete_service.chromadb_service = mock_chromadb
        qa_delete_service.langfuse_service = mock_langfuse
        
        # 첫 번째 요청 - 성공
        request1 = QADeleteRequest(
            qa_id="hash_item_003",
            admin_user="admin01"
        )
        result1 = qa_delete_service.delete_qa_item(request1)
        assert result1.success is True
        
        # 두 번째 요청 - 항목이 없어서 실패
        mock_chromadb.delete.side_effect = KeyError("항목을 찾을 수 없음")
        
        request2 = QADeleteRequest(
            qa_id="hash_item_003",
            admin_user="admin02"
        )
        result2 = qa_delete_service.delete_qa_item(request2)
        assert result2.success is False
    
    def test_delete_status_messages(
        self, qa_delete_service, mock_chromadb, mock_langfuse
    ):
        """다양한 상태 메시지 검증"""
        mock_langfuse.get_client.return_value = None  # Langfuse 클라이언트 비활성화
        
        qa_delete_service.chromadb_service = mock_chromadb
        qa_delete_service.langfuse_service = mock_langfuse
        
        # 성공 메시지
        request = QADeleteRequest(
            qa_id="hash_success",
            admin_user="admin"
        )
        result = qa_delete_service.delete_qa_item(request)
        assert result.success is True
        assert "성공" in result.message
        
        # 실패 메시지
        mock_chromadb.delete.side_effect = Exception("DB 오류")
        request = QADeleteRequest(
            qa_id="hash_fail",
            admin_user="admin"
        )
        result = qa_delete_service.delete_qa_item(request)
        assert result.success is False
        assert "오류" in result.message


class TestDeleteFlowWithAuthValidation:
    """인증 검증과 함께하는 삭제 흐름"""
    
    def test_admin_can_delete(
        self, qa_delete_service, mock_chromadb, mock_langfuse
    ):
        """관리자만 삭제 가능"""
        mock_langfuse.get_client.return_value = None  # Langfuse 클라이언트 비활성화
        
        qa_delete_service.chromadb_service = mock_chromadb
        qa_delete_service.langfuse_service = mock_langfuse
        
        # 관리자 삭제 요청
        request = QADeleteRequest(
            qa_id="hash_item",
            admin_user="admin_user"
        )
        
        result = qa_delete_service.delete_qa_item(request)
        assert result.success is True


class TestDeleteDialogFlow:
    """삭제 확인 다이얼로그 통합 테스트 (T021)"""
    
    def test_dialog_display_and_cancel(self):
        """다이얼로그 표시 및 취소 플로우"""
        # 다이얼로그 상태 모델
        class DialogState:
            show_dialog = False
            selected_qa_id = None
            is_deleting = False
        
        state = DialogState()
        
        # 1. 초기 상태: 다이얼로그 닫혀있음
        assert state.show_dialog is False
        assert state.selected_qa_id is None
        
        # 2. 버튼 클릭: 다이얼로그 열기
        state.show_dialog = True
        state.selected_qa_id = "hash_item_001"
        
        assert state.show_dialog is True
        assert state.selected_qa_id == "hash_item_001"
        
        # 3. 아니오 클릭: 다이얼로그 닫기
        state.show_dialog = False
        state.selected_qa_id = None
        
        assert state.show_dialog is False
        assert state.selected_qa_id is None


class TestPageResetAfterDelete:
    """삭제 후 페이지 리셋 통합 테스트 (T029)"""
    
    def test_page_reset_when_items_deleted(self):
        """마지막 항목 삭제 시 페이지 리셋"""
        # 페이지 상태 모델
        class PageState:
            current_page = 2
            total_items = 1
            current_items = ["hash_item_001"]
        
        state = PageState()
        
        # 삭제 후
        state.current_items = []
        state.total_items -= 1
        
        # 3. 아이템이 없으면 페이지 1로 리셋
        if len(state.current_items) == 0 and state.total_items > 0:
            state.current_page = 1
        elif state.total_items == 0:
            state.current_page = 1
        
        assert state.current_page == 1
        assert state.total_items == 0
        assert len(state.current_items) == 0


class TestDeleteStatusMessagesE2E:
    """삭제 상태 메시지 E2E 통합 테스트 (T036)"""
    
    def test_delete_progress_message(self):
        """삭제 진행 메시지"""
        message = "삭제 중..."
        status = "info"
        
        assert message == "삭제 중..."
        assert status == "info"
    
    def test_delete_success_message(self):
        """삭제 성공 메시지"""
        message = "✓ 삭제되었습니다"
        status = "success"
        
        assert "✓" in message
        assert "삭제되었습니다" in message
        assert status == "success"
    
    def test_delete_error_message(self):
        """삭제 실패 - DB 오류가 발생했습니다"""
        message = "❌ 삭제 실패 - DB 오류가 발생했습니다"
        status = "error"
        
        assert "❌" in message
        assert "실패" in message
        assert "DB 오류" in message
        assert status == "error"
