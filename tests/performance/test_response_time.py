"""Basic response-time oriented tests for cache performance."""

import time
from src.services.cache_service import CacheService
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
