"""삭제 상태 메시지 매핑 단위 테스트"""

from unittest.mock import Mock

from src.models.qa_delete_models import QADeleteRequest
from src.services.qa_delete_service import QADeleteService


def _make_service_with_mock(side_effect=None):
    QADeleteService._instance = None
    service = QADeleteService()
    chromadb = Mock()
    if side_effect is not None:
        chromadb.delete.side_effect = side_effect
    service.chromadb_service = chromadb
    service.langfuse_service = Mock()
    service.qa_list_service = Mock()
    return service


def test_delete_message_for_not_found_error():
    service = _make_service_with_mock(KeyError("항목을 찾을 수 없습니다"))

    result = service.delete_qa_item(QADeleteRequest(qa_id="hash1", admin_user="admin"))

    assert result.success is False
    assert result.message == "Q&A 항목을 찾을 수 없습니다"


def test_delete_message_for_network_error():
    service = _make_service_with_mock(Exception("network disconnected"))

    result = service.delete_qa_item(QADeleteRequest(qa_id="hash1", admin_user="admin"))

    assert result.success is False
    assert result.message == "네트워크 오류가 발생했습니다"


def test_delete_message_for_generic_error():
    service = _make_service_with_mock(Exception("db failure"))

    result = service.delete_qa_item(QADeleteRequest(qa_id="hash1", admin_user="admin"))

    assert result.success is False
    assert result.message == "Q&A 항목 삭제 중 오류가 발생했습니다"
