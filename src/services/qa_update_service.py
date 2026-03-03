"""
QA 업데이트 서비스 - 관리자가 Q&A를 추가/수정
Spec US3: 관리자가 Q&A를 추가/수정하고 ChromaDB를 업데이트
Spec FR-008: 중복 질문은 기존 항목 덮어쓰기
Spec FR-010: 관리자 입력 제한 (질문 500자, 답변 2000자)
"""
import logging
from typing import Dict, Tuple, Optional
from src.models.qa_item import QAItem
from src.services.file_service import FileService
from src.services.chromadb_service import ChromaDBService
from src.services.langfuse_service import get_langfuse_service
from src.config import MAX_ADMIN_QUESTION_LENGTH, MAX_ADMIN_ANSWER_LENGTH

logger = logging.getLogger(__name__)


class QAUpdateService:
    """Q&A 업데이트 관리 서비스 (US3)"""
    
    def __init__(self):
        """QA 업데이트 서비스 초기화"""
        self.file_service = FileService()
        self.chromadb = ChromaDBService()
        self.langfuse = get_langfuse_service()
    
    def validate_input(self, question: Optional[str], answer: Optional[str]) -> Dict:
        """입력값 검증 (EC3, FR-010)
        
        Args:
            question: 질문 (최대 500자)
            answer: 답변 (최대 2000자)
            
        Returns:
            {'valid': bool, 'error': str (실패 시)}
        """
        # None 체크
        if question is None or answer is None:
            return {'valid': False, 'error': '질문과 답변을 모두 입력해주세요'}
        
        # 타입 체크
        if not isinstance(question, str) or not isinstance(answer, str):
            return {'valid': False, 'error': '질문과 답변은 텍스트여야 합니다'}
        
        # 빈 값 또는 공백만 있는지 체크
        if not question.strip():
            return {'valid': False, 'error': '질문을 입력해주세요'}
        if not answer.strip():
            return {'valid': False, 'error': '답변을 입력해주세요'}
        
        # 길이 체크 (FR-010)
        if len(question) > MAX_ADMIN_QUESTION_LENGTH:
            return {
                'valid': False,
                'error': f'질문은 {MAX_ADMIN_QUESTION_LENGTH}자 이하여야 합니다'
            }
        
        if len(answer) > MAX_ADMIN_ANSWER_LENGTH:
            return {
                'valid': False,
                'error': f'답변은 {MAX_ADMIN_ANSWER_LENGTH}자 이하여야 합니다'
            }
        
        return {'valid': True}
    
    def add_or_update_qa(
        self,
        question: str,
        answer: str,
        metadata: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """Q&A 항목 추가 또는 업데이트 (US3, FR-008)
        
        Spec:
        - 중복 질문이면 기존 항목 덮어쓰기 (FR-008)
        - 새 항목이면 추가
        - 메타데이터 포함 가능
        
        Args:
            question: 질문 (정규화됨)
            answer: 답변 텍스트
            metadata: 추가 메타데이터 (optional)
            
        Returns:
            (성공 여부, 메시지)
        """
        # 입력값 검증
        validation = self.validate_input(question, answer)
        if not validation['valid']:
            logger.warning(f"Input validation failed: {validation['error']}")
            return False, validation['error']
        
        try:
            # 질문 정규화 (공백 제거)
            normalized_q = question.strip()
            
            # 기존 항목 여부 확인 (파일에서)
            try:
                existing_items = self.file_service.read_qa_items()
                target_key = normalized_q.lower()
                is_new = not any(item.get_hash_key() == target_key for item in existing_items)
            except Exception:
                is_new = True
            
            # QAItem 생성
            item = QAItem(
                question=normalized_q,
                answer=answer.strip(),
                metadata=metadata or {}
            )
            
            # 파일에 업데이트 (중복 질문이면 덮어쓰기)
            self.file_service.update_or_insert_qa_item(item)
            
            # ChromaDB에 업데이트
            self.chromadb.update_qa_item(item)
            
            # Langfuse 추적
            self.langfuse.log_qa_update(
                question_length=len(normalized_q),
                answer_length=len(answer),
                is_new=is_new
            )
            
            # 성공 메시지
            action = "추가" if is_new else "수정"
            msg = f"✓ Q&A {action}되었습니다"
            logger.info(f"QA item {action}: {normalized_q[:50]}...")
            
            return True, msg
            
        except Exception as e:
            logger.error(f"Error updating QA item: {e}")
            self.langfuse.log_error(
                error_type="qa_update_failed",
                error_message=str(e)
            )
            return False, f"✗ 오류 발생: {str(e)}"
    
    def _question_exists(self, question: str) -> bool:
        """질문이 이미 존재하는지 확인
        
        Args:
            question: 확인할 질문
            
        Returns:
            존재 여부
        """
        # 간단하게 구현
        # 실제로는 ChromaDB에서 확인
        try:
            results = self.chromadb.search_similar(question, top_k=1)
            return len(results) > 0 and results[0]['similarity'] > 0.99
        except Exception:
            return False


# 글로벌 인스턴스
_qa_update_service: Optional[QAUpdateService] = None


def get_qa_update_service() -> QAUpdateService:
    """QA 업데이트 서비스 인스턴스 반환 (싱글톤)
    
    Returns:
        QAUpdateService 인스턴스
    """
    global _qa_update_service
    if _qa_update_service is None:
        _qa_update_service = QAUpdateService()
    return _qa_update_service
