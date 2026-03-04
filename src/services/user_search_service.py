"""
사용자 질문 검색 서비스
Spec US4: 사용자가 질문을 입력하면 ChromaDB에서 유사한 QA를 검색하여 반환
Spec FR-003: 검색 결과는 정확한 정보만 반환 (환상화 방지)
Spec FR-004: 유사도 임계값 0.7 이상만 반환
Spec FR-009: 사용자는 최대 1개 검색 결과만 반환
"""
import logging
from typing import Dict, List, Optional
from src.services.chromadb_service import ChromaDBService
from src.services.langfuse_service import get_langfuse_service
from src.config import SIMILARITY_THRESHOLD, SEARCH_TOP_K_USER, MAX_USER_QUESTION_LENGTH

logger = logging.getLogger(__name__)


class UserSearchService:
    """사용자 질문 검색 서비스 (US4)"""
    
    def __init__(self):
        """검색 서비스 초기화"""
        self.chromadb = ChromaDBService()
        self.langfuse = get_langfuse_service()
    
    def validate_search_query(self, query: Optional[str]) -> Dict:
        """검색 쿼리 검증
        
        Args:
            query: 검색어
            
        Returns:
            {'valid': bool, 'error': str (실패 시)}
        """
        # None 체크
        if query is None:
            return {'valid': False, 'error': '검색어를 입력해주세요'}
        
        # 타입 체크
        if not isinstance(query, str):
            return {'valid': False, 'error': '검색어는 텍스트여야 합니다'}
        
        # 빈 값 또는 공백만 있는지 체크
        if not query.strip():
            return {'valid': False, 'error': '검색어를 입력해주세요'}

        # 길이 제한 체크
        if len(query) > MAX_USER_QUESTION_LENGTH:
            return {
                'valid': False,
                'error': f'질문은 {MAX_USER_QUESTION_LENGTH}자 이내여야 합니다'
            }

        return {'valid': True}
    
    def search_qa(self, query: str) -> List[Dict]:
        """Q&A 검색 (US4, FR-003, FR-004, FR-009)
        
        Spec:
        - 검색 쿼리 기반으로 ChromaDB에서 유사도 검색
        - 유사도 임계값 0.7 이상만 반환 (FR-004)
        - 사용자는 최대 1개 결과만 반환 (FR-009)
        - 정확한 정보만 반환 (환상화 방지, FR-003)
        
        Args:
            query: 검색어
            
        Returns:
            검색 결과 리스트 (최대 1개)
            [{"question": str, "answer": str, "similarity": float}, ...]
        """
        # 입력값 검증
        validation = self.validate_search_query(query)
        if not validation['valid']:
            logger.warning(f"Search query validation failed: {validation['error']}")
            return []
        
        try:
            # ChromaDB에서 최대 1개 결과 검색 (FR-009)
            results = self.chromadb.search_similar(query, top_k=SEARCH_TOP_K_USER)
            
            # 결과 변환 및 필터링
            output = []
            for result in results:
                # 유사도 임계값 확인 (FR-004)
                # 이미 search_similar에서 필터링되지만 명시적으로 재확인
                if result.get('similarity', 0) >= SIMILARITY_THRESHOLD:
                    # 사용자에게 표시할 정보만 추출 (FR-003: 정확한 정보만)
                    output.append({
                        'answer': result.get('answer', '답변을 찾을 수 없습니다'),
                        'similarity': result.get('similarity', 0),
                        'question': result.get('question', '')  # 참고용
                    })
            
            # Langfuse 로깅
            self.langfuse.log_user_search(
                question_length=len(query),
                num_results=len(output),
                top_similarity=output[0]['similarity'] if output else 0.0
            )
            
            logger.info(f"User search for '{query}' returned {len(output)} result(s)")
            return output
            
        except Exception as e:
            logger.error(f"Error searching QA: {e}")
            self.langfuse.log_error(
                error_type="user_search_failed",
                error_message=str(e)
            )
            return []


# 글로벌 인스턴스
_user_search_service: Optional[UserSearchService] = None


def get_user_search_service() -> UserSearchService:
    """사용자 검색 서비스 인스턴스 반환 (싱글톤)
    
    Returns:
        UserSearchService 인스턴스
    """
    global _user_search_service
    if _user_search_service is None:
        _user_search_service = UserSearchService()
    return _user_search_service
