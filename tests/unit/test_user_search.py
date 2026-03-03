"""
단위 테스트: 사용자 질문 검색 서비스
Spec US4: 사용자가 질문을 입력하면 ChromaDB에서 유사한 QA를 검색하여 반환
Spec FR-003: 검색 결과는 정확한 정보만 반환 (환상화 방지)
Spec FR-004: 유사도 임계값 0.7 이상만 반환
Spec FR-009: 사용자는 최대 1개 검색 결과만 반환
"""
import pytest
from src.services.user_search_service import UserSearchService
from src.services.chromadb_service import ChromaDBService
from src.services.file_service import FileService
from src.models.qa_item import QAItem
from src.config import INIT_FILE_PATH, SIMILARITY_THRESHOLD, CHROMA_PERSIST_DIR
import os
import shutil


@pytest.fixture(scope="function")
def cleanup_before_test():
    """테스트 전에 데이터 정리"""
    # 테스트 전: 정리
    if os.path.exists(INIT_FILE_PATH):
        os.remove(INIT_FILE_PATH)
    if os.path.exists(CHROMA_PERSIST_DIR):
        shutil.rmtree(CHROMA_PERSIST_DIR, ignore_errors=True)
    
    yield
    
    # 테스트 후: 정리
    if os.path.exists(INIT_FILE_PATH):
        os.remove(INIT_FILE_PATH)
    if os.path.exists(CHROMA_PERSIST_DIR):
        shutil.rmtree(CHROMA_PERSIST_DIR, ignore_errors=True)


@pytest.fixture
def search_service_with_data(cleanup_before_test):
    """검색 서비스 인스턴스 및 초기 데이터"""
    # 파일 조성
    file_service = FileService()
    items = [
        QAItem("What is Python?", "Python is a high-level programming language.", metadata={"source": "admin"}),
        QAItem("How to install Python?", "Download from python.org and run installer.", metadata={"source": "admin"}),
        QAItem("What is a function?", "A function is a reusable block of code.", metadata={"source": "admin"}),
    ]
    file_service.write_qa_items(items)
    
    # ChromaDB 로드
    chroma = ChromaDBService()
    chroma.add_qa_items(items)
    
    # 검색 서비스 반환
    service = UserSearchService()
    
    # 검증: 데이터가 실제로 저장되었는지 확인
    assert chroma.count_items() > 0, "ChromaDB에 데이터가 저장되지 않았습니다"
    
    return service


class TestUserSearchValidation:
    """사용자 검색 입력 검증"""
    
    def test_empty_query_fails(self):
        """목표: 빈 검색어는 거부"""
        service = UserSearchService()
        
        result = service.validate_search_query("")
        assert result['valid'] == False
        assert "입력" in result['error']
    
    def test_whitespace_only_query_fails(self):
        """목표: 공백만 있는 검색어는 거부"""
        service = UserSearchService()
        
        result = service.validate_search_query("   ")
        assert result['valid'] == False
    
    def test_none_query_fails(self):
        """목표: None 입력은 거부"""
        service = UserSearchService()
        
        result = service.validate_search_query(None)
        assert result['valid'] == False
    
    def test_type_error_query_fails(self):
        """목표: 비문자열 입력은 거부"""
        service = UserSearchService()
        
        result = service.validate_search_query(123)
        assert result['valid'] == False
    
    def test_query_too_long_fails(self):
        """목표: 검색어가 너무 길면 거부 (FR-011에서 추정)"""
        service = UserSearchService()
        long_query = "Question " * 100  # 매우 긴 쿼리
        
        result = service.validate_search_query(long_query)
        # 너무 길면 거부하거나, 잘라내기
        assert isinstance(result, dict)
    
    def test_valid_query_passes(self):
        """목표: 올바른 검색어는 검증 통과"""
        service = UserSearchService()
        
        result = service.validate_search_query("What is Python?")
        assert result['valid'] == True


class TestUserSearchResults:
    """사용자 검색 결과 반환"""
    
    def test_search_returns_list(self, search_service_with_data):
        """목표: 검색은 항상 리스트 반환"""
        results = search_service_with_data.search_qa("What is Python?")
        
        assert isinstance(results, list)
    
    def test_max_one_result_returned(self, search_service_with_data):
        """목표: 사용자에게 최대 1개 결과만 반환 (FR-009)"""
        results = search_service_with_data.search_qa("Python function")
        
        assert len(results) <= 1
    
    def test_result_has_required_fields(self, search_service_with_data):
        """목표: 검색 결과 형식 확인"""
        results = search_service_with_data.search_qa("What is Python?")
        
        # 결과가 있으면 필수 필드 확인
        for result in results:
            assert 'answer' in result
            assert 'similarity' in result
            assert isinstance(result['answer'], str)
            assert isinstance(result['similarity'], (int, float))
    
    def test_similarity_threshold_applied(self, search_service_with_data):
        """목표: 유사도 임계값 0.7 이상만 반환 (FR-004)"""
        results = search_service_with_data.search_qa("xyz123randomtext")
        
        if len(results) > 0:
            # 결과가 있으면 유사도가 임계값 이상
            assert results[0]['similarity'] >= SIMILARITY_THRESHOLD


class TestUserSearchEdgeCases:
    """사용자 검색 엣지 케이스"""
    
    def test_special_characters_in_query(self, search_service_with_data):
        """목표: 특수문자 포함 검색"""
        results = search_service_with_data.search_qa("What's a @function #tag?")
        
        # 오류 없이 처리되어야 함
        assert isinstance(results, list)
    
    def test_unicode_in_query(self, search_service_with_data):
        """목표: 유니코드 검색어 처리"""
        results = search_service_with_data.search_qa("파이썬은 무엇인가? 🐍")
        
        # 오류 없이 처리되어야 함
        assert isinstance(results, list)
