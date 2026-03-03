"""Integration tests for cache with services."""

import pytest
from src.services.cache_service import CacheService, get_cache_service, reset_cache_service
from src.utils.cache import LRUCache, reset_cache
from src.models.cache_models import CacheStats


class TestCacheServiceIntegration:
    """캐시 서비스 통합 테스트"""
    
    def setup_method(self):
        """각 테스트마다 새로운 서비스"""
        reset_cache()
        self.service = CacheService()
        self.embedding = [0.1] * 1536
    
    def test_cache_service_stores_embedding(self):
        """캐시 서비스가 임베딩을 저장"""
        question = "테스트 질문"
        
        self.service.set_embedding(question, self.embedding)
        result = self.service.get_embedding(question)
        
        assert result == self.embedding
    
    def test_cache_service_hit_miss(self):
        """캐시 hit/miss 추적"""
        question = "테스트 질문"
        missing_question = "없는 질문"
        
        self.service.set_embedding(question, self.embedding)
        _ = self.service.get_embedding(question)  # hit
        _ = self.service.get_embedding(missing_question)  # miss
        
        stats = self.service.get_stats()
        assert stats["cache_hits"] == 1
        assert stats["cache_misses"] == 1
    
    def test_cache_service_clear(self):
        """캐시 서비스 clear"""
        question = "테스트 질문"
        
        self.service.set_embedding(question, self.embedding)
        assert self.service.get_embedding(question) is not None
        
        self.service.clear()
        assert self.service.get_embedding(question) is None
    
    def test_cache_service_stats(self):
        """캐시 서비스 통계"""
        question = "테스트 질문"
        
        self.service.set_embedding(question, self.embedding)
        self.service.get_embedding(question)
        self.service.get_embedding(question)
        
        stats = self.service.get_stats()
        assert stats["cache_size"] == 1
        assert stats["total_requests"] == 2
        assert stats["cache_hits"] == 2
        assert stats["hit_ratio_percent"] == 100.0
    
    def test_cache_service_singleton(self):
        """캐시 서비스 싱글톤"""
        reset_cache_service()
        
        service1 = get_cache_service()
        question = "테스트"
        service1.set_embedding(question, self.embedding)
        
        service2 = get_cache_service()
        result = service2.get_embedding(question)
        
        assert result == self.embedding


class TestCacheServiceWithDifferentQuestions:
    """다양한 질문에 대한 캐시 테스트"""
    
    def setup_method(self):
        reset_cache()
        self.service = CacheService()
    
    def test_different_questions_cached_separately(self):
        """다른 질문은 별도로 캐시됨"""
        questions = [
            "Python이 뭐야?",
            "Docker는 뭐야?",
            "임베딩이 뭐야?"
        ]
        embeddings = [
            [0.1] * 1536,
            [0.2] * 1536,
            [0.3] * 1536,
        ]
        
        for q, emb in zip(questions, embeddings):
            self.service.set_embedding(q, emb)
        
        for q, emb in zip(questions, embeddings):
            result = self.service.get_embedding(q)
            assert result == emb
    
    def test_cache_with_unicode_questions(self):
        """유니코드 질문 처리"""
        questions = [
            "Python이 뭐야?",
            "Java는 뭐야?",
            "C++은 뭐야?",
            "Rust를 배우고 싶어",
            "Go 언어 어떻게 배워?",
        ]
        
        for q in questions:
            embedding = [hash(q) % 256 / 256 for _ in range(1536)]
            self.service.set_embedding(q, embedding)
        
        # 모두 조회 가능
        for q in questions:
            result = self.service.get_embedding(q)
            assert result is not None
    
    def test_normalized_questions_same_cache(self):
        """정규화된 질문은 같은 캐시 사용"""
        question1 = "테스트 질문"
        question2 = "  테스트  질문  "  # 공백 다름
        
        embedding = [0.1] * 1536
        self.service.set_embedding(question1, embedding)
        
        # question2는 question1과 동일하게 정규화되어 캐시 히트
        result = self.service.get_embedding(question2)
        assert result == embedding
        
        stats = self.service.get_stats()
        assert stats["cache_hits"] == 1
        assert stats["cache_misses"] == 0


class TestCacheResponseTime:
    """응답 시간 추적 테스트"""
    
    def setup_method(self):
        reset_cache()
        self.service = CacheService()
    
    def test_response_time_tracking(self):
        """응답 시간이 추적됨"""
        question = "테스트"
        embedding = [0.1] * 1536
        
        self.service.set_embedding(question, embedding)
        _ = self.service.get_embedding(question)
        
        stats = self.service.get_stats()
        # 응답 시간이 기록됨 (0초 이상)
        assert stats["avg_response_time_ms"] >= 0
    
    def test_avg_response_time_calculation(self):
        """평균 응답 시간 계산"""
        question = "테스트"
        embedding = [0.1] * 1536
        
        self.service.set_embedding(question, embedding)
        
        # 여러 번 조회
        for _ in range(5):
            _ = self.service.get_embedding(question)
        
        stats = self.service.get_stats()
        # 캐시 히트는 매우 빠름 (<1ms)
        assert stats["avg_response_time_ms"] < 10  # 10ms 이하


class TestCacheMemoryUsage:
    """메모리 사용량 추적 테스트"""
    
    def setup_method(self):
        reset_cache()
        self.service = CacheService()
    
    def test_memory_increases_with_items(self):
        """항목 추가 시 메모리 증가"""
        stats1 = self.service.get_stats()
        initial_memory = stats1["memory_used_mb"]
        
        embedding = [0.1] * 1536
        for i in range(100):
            question = f"질문{i}"
            self.service.set_embedding(question, embedding)
        
        stats2 = self.service.get_stats()
        final_memory = stats2["memory_used_mb"]
        
        # 100개 항목 = ~0.6MB
        assert final_memory > initial_memory
        assert 0.5 < final_memory < 1.0


class TestCacheInMultipleServices:
    """여러 서비스에서 캐시 공유"""
    
    def test_cache_shared_across_services(self):
        """캐시는 모든 서비스에서 공유"""
        reset_cache()
        reset_cache_service()
        
        service1 = get_cache_service()
        service2 = get_cache_service()
        
        question = "테스트"
        embedding = [0.1] * 1536
        
        service1.set_embedding(question, embedding)
        result = service2.get_embedding(question)
        
        # 같은 캐시 인스턴스
        assert result == embedding
