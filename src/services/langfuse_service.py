"""
Langfuse 추적 및 로깅 서비스
"""
from typing import Any, Dict, Optional
import logging
from src.config import LANGFUSE_API_KEY, LANGFUSE_HOST

logger = logging.getLogger(__name__)


class LangfuseService:
    """Langfuse를 통한 관찰성(Observability) 제공
    
    헌법 원칙: 관찰성 - 모든 주요 작업을 Langfuse로 추적
    """
    
    def __init__(self, api_key: Optional[str] = None, host: Optional[str] = None):
        """Langfuse 서비스 초기화
        
        Args:
            api_key: Langfuse API 키 (기본: config.LANGFUSE_API_KEY)
            host: Langfuse 호스트 (기본: config.LANGFUSE_HOST)
        """
        self.api_key = api_key or LANGFUSE_API_KEY
        self.host = host or LANGFUSE_HOST
        self.client = None
        
        # API 키가 설정되어 있으면 초기화
        if self.api_key:
            self._initialize_client()
        else:
            logger.warning("Langfuse API key not configured, observability disabled")
    
    def _initialize_client(self) -> None:
        """Langfuse 클라이언트 초기화"""
        try:
            # TODO: research.md에서 최종 결정 후 구현
            # from langfuse import Langfuse
            # self.client = Langfuse(api_key=self.api_key, host=self.host)
            
            logger.info(f"Langfuse service initialized (host: {self.host})")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Langfuse: {e}")
    
    def log_event(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """이벤트 로깅 (헌법 관찰성 구현)

        표준 필드:
        - event_type
        - success
        - error_message (오류 시)
        """
        payload = {
            "event_type": name,
            "success": True,
            "error_message": None,
            **(metadata or {}),
        }

        if not self.api_key or not self.client:
            logger.debug(f"Event (no Langfuse): {payload}")
            return

        try:
            # TODO: Langfuse 클라이언트 구현 후 활성화
            # self.client.log(name=name, metadata=payload)
            logger.debug(f"Logged event to Langfuse: {name}")

        except Exception as e:
            logger.warning(f"Error logging event to Langfuse: {e}")
    
    def log_initial_load(self, num_items: int, duration_ms: float, success: bool) -> None:
        """초기 로드 이벤트 추적 (US1)
        
        Args:
            num_items: 로드된 항목 수
            duration_ms: 소요 시간 (밀리초)
            success: 성공 여부
        """
        self.log_event("initial_load", {
            "event_type": "initial_load",
            "num_items": num_items,
            "duration_ms": round(duration_ms, 2),
            "success": success
        })
    
    def log_admin_login(self, success: bool, reason: Optional[str] = None) -> None:
        """관리자 로그인 시도 추적 (US2)

        Args:
            success: 성공 여부
            reason: 실패 사유 (성공 시 None)
        """
        self.log_event("admin_login", {
            "event_type": "admin_login",
            "success": success,
            "reason": reason,
            "error_message": None if success else reason
        })

    def log_admin_logout(self, success: bool = True) -> None:
        """관리자 로그아웃 이벤트 추적 (US2)."""
        self.log_event("admin_logout", {
            "event_type": "admin_logout",
            "success": success,
            "error_message": None if success else "logout_failed"
        })
    
    def log_qa_update(self, question_length: int, answer_length: int, is_new: bool) -> None:
        """Q&A 업데이트 이벤트 추적 (US3)
        
        Args:
            question_length: 질문 길이
            answer_length: 답변 길이
            is_new: 신규 항목 여부 (False면 기존 항목 덮어쓰기)
        """
        self.log_event("qa_update", {
            "event_type": "qa_update",
            "success": True,
            "question_length": question_length,
            "answer_length": answer_length,
            "is_new": is_new
        })
    
    def log_user_search(self, question_length: int, num_results: int, top_similarity: Optional[float] = None) -> None:
        """사용자 검색 이벤트 추적 (US4)
        
        Args:
            question_length: 질문 길이
            num_results: 반환된 결과 수 (0~1)
            top_similarity: 최상위 결과의 유사도
        """
        self.log_event("user_search", {
            "event_type": "user_search",
            "success": True,
            "question_length": question_length,
            "num_results": num_results,
            "top_similarity": round(top_similarity, 4) if top_similarity else None
        })
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """에러 로깅 (헌법 관찰성)
        
        Args:
            error_type: 에러 타입 (예: "invalid_password", "file_read_error")
            error_message: 에러 메시지
            context: 추가 컨텍스트
        """
        self.log_event("error", {
            "event_type": "error",
            "success": False,
            "error_type": error_type,
            "error_message": error_message,
            **(context or {})
        })
    
    def log_qa_deleted(self, qa_id: str, admin_user: str, timestamp: Any) -> None:
        """Q&A 항목 삭제 추적 (Feature 002)
        
        Args:
            qa_id: 삭제된 Q&A 항목 ID
            admin_user: 삭제 작업 수행 관리자
            timestamp: 삭제 시간
        """
        self.log_event("qa_deleted", {
            "event_type": "qa_deleted",
            "qa_id": qa_id,
            "admin_user": admin_user,
            "timestamp": str(timestamp),
            "success": True
        })
    
    def log_performance(self, operation: str, duration_ms: float) -> None:
        """성능 메트릭 로깅
        
        Args:
            operation: 작업 이름 (예: "embedding_generation", "chromadb_search")
            duration_ms: 소요 시간 (밀리초)
        """
        self.log_event("performance", {
            "operation": operation,
            "duration_ms": round(duration_ms, 2)
        })


# 글로벌 인스턴스
_langfuse_service: Optional[LangfuseService] = None


def get_langfuse_service() -> LangfuseService:
    """Langfuse 서비스 인스턴스 반환 (싱글톤)
    
    Returns:
        LangfuseService 인스턴스
    """
    global _langfuse_service
    if _langfuse_service is None:
        _langfuse_service = LangfuseService()
    return _langfuse_service
