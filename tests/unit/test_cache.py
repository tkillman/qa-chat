"""Unit tests for LRU Cache implementation."""

import pytest
from src.utils.cache import LRUCache, get_cache, reset_cache
from src.models.cache_models import CacheEntry, CacheStats


class TestLRUCacheBasics:
    """기본 캐시 동작 테스트"""
    
    def setup_method(self):
        """각 테스트마다 새로운 캐시 생성"""
        self.cache = LRUCache(max_size=3)
        self.embedding = [0.1] * 1536
    
    def test_cache_set_and_get(self):
        """캐시에 저장하고 조회"""
        key = LRUCache.hash_question("테스트")
        
        self.cache.set(key, self.embedding)
        result = self.cache.get(key)
        
        assert result == self.embedding
        assert len(self.cache) == 1
    
    def test_cache_get_nonexistent(self):
        """존재하지 않는 키 조회"""
        key = LRUCache.hash_question("없는 키")
        result = self.cache.get(key)
        
        assert result is None
    
    def test_cache_clear(self):
        """캐시 초기화"""
        key = LRUCache.hash_question("테스트")
        self.cache.set(key, self.embedding)
        assert len(self.cache) == 1
        
        self.cache.clear()
        assert len(self.cache) == 0
        assert self.cache.get(key) is None


class TestLRUEviction:
    """LRU 제거 정책 테스트"""
    
    def setup_method(self):
        """최대 3개 항목만 허용하는 캐시"""
        self.cache = LRUCache(max_size=3)
        self.embedding = [0.1] * 1536
    
    def test_lru_eviction_when_full(self):
        """캐시가 가득 차면 가장 오래된 항목 제거"""
        key1 = LRUCache.hash_question("질문1")
        key2 = LRUCache.hash_question("질문2")
        key3 = LRUCache.hash_question("질문3")
        key4 = LRUCache.hash_question("질문4")
        
        self.cache.set(key1, self.embedding)
        self.cache.set(key2, self.embedding)
        self.cache.set(key3, self.embedding)
        assert len(self.cache) == 3
        
        # 4번째 항목 추가 → 첫 번째 항목 제거
        self.cache.set(key4, self.embedding)
        assert len(self.cache) == 3
        assert self.cache.get(key1) is None  # 제거됨
        assert self.cache.get(key4) is not None  # 새 항목 있음
    
    def test_lru_reuse_moves_to_end(self):
        """항목 재사용 시 최신 위치로 이동"""
        key1 = LRUCache.hash_question("질문1")
        key2 = LRUCache.hash_question("질문2")
        key3 = LRUCache.hash_question("질문3")
        key4 = LRUCache.hash_question("질문4")
        
        self.cache.set(key1, self.embedding)
        self.cache.set(key2, self.embedding)
        self.cache.set(key3, self.embedding)
        
        # key1 재접근 → 최신 위치로 이동
        self.cache.get(key1)
        
        # key4 추가 → key2가 제거됨 (가장 오래됨)
        self.cache.set(key4, self.embedding)
        assert self.cache.get(key1) is not None
        assert self.cache.get(key2) is None  # 제거됨
        assert self.cache.get(key4) is not None


class TestCacheValidation:
    """입력 검증 테스트"""
    
    def setup_method(self):
        self.cache = LRUCache()
        self.embedding = [0.1] * 1536
    
    def test_invalid_key_length(self):
        """잘못된 크기의 키"""
        with pytest.raises(ValueError, match="SHA256"):
            self.cache.set("short_key", self.embedding)
        
        with pytest.raises(ValueError, match="SHA256"):
            self.cache.get("short_key")
    
    def test_invalid_embedding_size(self):
        """잘못된 크기의 임베딩"""
        key = LRUCache.hash_question("테스트")
        
        with pytest.raises(ValueError, match="1536"):
            self.cache.set(key, [0.1] * 100)  # 너무 작음
        
        with pytest.raises(ValueError, match="1536"):
            self.cache.set(key, [0.1] * 2000)  # 너무 큼
    
    def test_invalid_embedding_type(self):
        """임베딩이 리스트가 아님"""
        key = LRUCache.hash_question("테스트")
        
        with pytest.raises(ValueError):
            self.cache.set(key, "not_a_list")


class TestCacheStats:
    """통계 추적 테스트"""
    
    def setup_method(self):
        self.cache = LRUCache()
        self.embedding = [0.1] * 1536
        self.key = LRUCache.hash_question("테스트")
    
    def test_hit_ratio_calculation(self):
        """히트율 계산"""
        self.cache.set(self.key, self.embedding)
        
        self.cache.get(self.key)  # 히트
        self.cache.get(LRUCache.hash_question("없는키"))  # 미스
        
        stats = self.cache.get_stats()
        assert stats.hit_ratio == 50.0  # 1 hit / 2 total
        assert stats.miss_ratio == 50.0
    
    def test_stats_counters(self):
        """통계 카운터"""
        self.cache.set(self.key, self.embedding)
        
        self.cache.get(self.key)
        self.cache.get(self.key)
        self.cache.get(self.key)
        
        stats = self.cache.get_stats()
        assert stats.total_requests == 3
        assert stats.cache_hits == 3
        assert stats.cache_misses == 0
    
    def test_cache_size_tracking(self):
        """캐시 크기 추적"""
        stats = self.cache.get_stats()
        assert stats.cache_size == 0
        
        self.cache.set(self.key, self.embedding)
        stats = self.cache.get_stats()
        assert stats.cache_size == 1
    
    def test_memory_usage_estimation(self):
        """메모리 사용량 추정"""
        stats = self.cache.get_stats()
        initial_memory = stats.memory_used_mb
        
        for i in range(100):
            key = LRUCache.hash_question(f"질문{i}")
            self.cache.set(key, self.embedding)
        
        stats = self.cache.get_stats()
        estimated_mb = stats.memory_used_mb
        
        # 100개 항목 ≈ 0.6MB
        assert 0.5 < estimated_mb < 1.0
    
    def test_reset_stats(self):
        """통계 초기화"""
        self.cache.set(self.key, self.embedding)
        self.cache.get(self.key)
        
        stats_before = self.cache.get_stats()
        assert stats_before.total_requests == 1
        
        self.cache.reset_stats()
        stats_after = self.cache.get_stats()
        assert stats_after.total_requests == 0
        assert stats_after.cache_size == 1  # 캐시는 유지


class TestCacheThreadSafety:
    """스레드 안전성 테스트"""
    
    def test_concurrent_access(self):
        """동시 접근 테스트"""
        import threading
        
        cache = LRUCache(max_size=1000)
        embedding = [0.1] * 1536
        errors = []
        
        def worker(thread_id):
            try:
                for i in range(10):
                    key = LRUCache.hash_question(f"질문_{thread_id}_{i}")
                    cache.set(key, embedding)
                    cache.get(key)
            except Exception as e:
                errors.append(e)
        
        # 10개 스레드에서 동시에 실행
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert len(cache) <= 1000  # 최대 크기 유지


class TestCacheHashQuestion:
    """질문 해싱 테스트"""
    
    def test_hash_consistency(self):
        """같은 질문은 같은 해시"""
        question = "테스트 질문"
        hash1 = LRUCache.hash_question(question)
        hash2 = LRUCache.hash_question(question)
        
        assert hash1 == hash2
    
    def test_hash_normalization(self):
        """공백과 대소문자 정규화"""
        hash1 = LRUCache.hash_question("테스트 질문")
        hash2 = LRUCache.hash_question("  테스트  질문  ")
        
        # 공백 정규화됨
        assert hash1 == hash2
    
    def test_hash_length(self):
        """해시 길이는 64 (SHA256)"""
        hash_value = LRUCache.hash_question("test")
        assert len(hash_value) == 64
        assert all(c in "0123456789abcdef" for c in hash_value)


class TestCacheSingleton:
    """싱글톤 인스턴스 테스트"""
    
    def test_get_cache_returns_same_instance(self):
        """get_cache()는 같은 인스턴스 반환"""
        reset_cache()
        
        cache1 = get_cache()
        cache2 = get_cache()
        
        assert cache1 is cache2
    
    def test_cache_persistence_across_calls(self):
        """캐시는 여러 호출 간 유지"""
        reset_cache()
        
        cache1 = get_cache()
        embedding = [0.1] * 1536
        key = LRUCache.hash_question("테스트")
        
        cache1.set(key, embedding)
        
        cache2 = get_cache()
        result = cache2.get(key)
        
        assert result == embedding
    
    def test_reset_clears_singleton(self):
        """reset_cache()는 싱글톤 클리어"""
        cache1 = get_cache()
        embedding = [0.1] * 1536
        key = LRUCache.hash_question("테스트")
        
        cache1.set(key, embedding)
        
        reset_cache()
        
        cache2 = get_cache()
        result = cache2.get(key)
        
        assert result is None  # 새 인스턴스라서 비어있음


class TestCacheLen:
    """__len__ 메서드 테스트"""
    
    def test_len_reflects_items(self):
        """len()은 항목 수를 반영"""
        cache = LRUCache()
        assert len(cache) == 0
        
        embedding = [0.1] * 1536
        for i in range(5):
            key = LRUCache.hash_question(f"질문{i}")
            cache.set(key, embedding)
            assert len(cache) == i + 1


class TestCacheCopyStats:
    """통계 복사 테스트"""
    
    def test_stats_are_independent(self):
        """반환된 통계는 독립적"""
        cache = LRUCache()
        embedding = [0.1] * 1536
        key = LRUCache.hash_question("테스트")
        
        cache.set(key, embedding)
        cache.get(key)
        
        stats1 = cache.get_stats()
        # stats1을 수정해도 캐시에 영향 없음
        stats1.cache_hits = 999
        
        stats2 = cache.get_stats()
        assert stats2.cache_hits == 1  # 원본 유지
