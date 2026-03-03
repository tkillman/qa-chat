"""Performance test for concurrent cache access (10+ users)."""

from concurrent.futures import ThreadPoolExecutor
from src.services.cache_service import CacheService
from src.utils.cache import reset_cache


def test_concurrent_10_users_cache_access():
    """10명의 동시 사용자가 캐시 접근 시 오류 없이 동작해야 함."""
    reset_cache()
    cache_service = CacheService()
    embedding = [0.1] * 1536

    # 사전 워밍업: 캐시 히트를 유도
    cache_service.set_embedding("동시성 테스트 질문", embedding)

    def worker(user_id: int):
        result = cache_service.get_embedding("동시성 테스트 질문")
        assert result is not None
        return user_id

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, i) for i in range(10)]
        results = [f.result() for f in futures]

    assert len(results) == 10
    stats = cache_service.get_stats()
    assert stats["cache_hits"] >= 10
