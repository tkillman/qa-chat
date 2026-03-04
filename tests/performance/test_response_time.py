"""Basic response-time oriented tests for cache performance."""

import time
from unittest.mock import Mock
from src.services.cache_service import CacheService
from src.services.qa_delete_service import QADeleteService
from src.models.qa_delete_models import QADeleteRequest
from src.utils.cache import reset_cache


def test_cache_hit_is_fast_enough():
    """캐시 히트 평균 시간은 100ms 미만이어야 함."""
    reset_cache()
    cache_service = CacheService()
    embedding = [0.1] * 1536
    question = "응답 속도 테스트"

    cache_service.set_embedding(question, embedding)

    start = time.perf_counter()
    for _ in range(100):
        result = cache_service.get_embedding(question)
        assert result is not None
    elapsed_ms = (time.perf_counter() - start) * 1000

    avg_ms = elapsed_ms / 100
    assert avg_ms < 100


def test_delete_response_is_under_2_seconds():
    """삭제 서비스 응답 시간은 2초 미만이어야 함."""
    QADeleteService._instance = None
    service = QADeleteService()

    service.chromadb_service = Mock()
    mock_langfuse = Mock()
    mock_langfuse.get_client.return_value = None
    service.langfuse_service = mock_langfuse
    service.qa_list_service = Mock()

    request = QADeleteRequest(qa_id="hash_perf", admin_user="admin")

    start = time.perf_counter()
    result = service.delete_qa_item(request)
    elapsed_seconds = time.perf_counter() - start

    assert result.success is True
    assert elapsed_seconds < 2.0
