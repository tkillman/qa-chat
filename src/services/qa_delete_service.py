"""
Q&A 항목 삭제 서비스
"""
import logging
from typing import Optional
from datetime import datetime

from src.models.qa_delete_models import QADeleteRequest, QADeleteResult

logger = logging.getLogger(__name__)


class QADeleteService:
    """Q&A 항목 삭제를 담당하는 싱글톤 서비스
    
    이 서비스는 ChromaDB에서 Q&A 항목을 삭제하고,
    Langfuse에 삭제 작업을 기록합니다.
    """
    
    _instance: Optional["QADeleteService"] = None
    
    def __new__(cls):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """서비스 초기화"""
        if self._initialized:
            return
        
        # 의존성 주입 (lazy loading)
        self.chromadb_service = None
        self.langfuse_service = None
        self.qa_list_service = None
        self._initialized = True
    
    def _ensure_dependencies(self):
        """의존성 가져오기"""
        if self.chromadb_service is None:
            from src.services.chromadb_service import ChromaDBService
            self.chromadb_service = ChromaDBService()
        
        if self.langfuse_service is None:
            from src.services.langfuse_service import LangfuseService
            self.langfuse_service = LangfuseService()
        
        if self.qa_list_service is None:
            from src.services.qa_list_service import QAListService
            self.qa_list_service = QAListService()
    
    def delete_qa_item(self, request: QADeleteRequest) -> QADeleteResult:
        """Q&A 항목 삭제
        
        Args:
            request: 삭제 요청 정보
        
        Returns:
            QADeleteResult: 삭제 작업 결과
        
        Raises:
            ValueError: 요청 데이터가 유효하지 않은 경우
        """
        self._ensure_dependencies()
        
        try:
            # 요청 유효성 검사
            if not request.qa_id or not request.admin_user:
                raise ValueError("qa_id와 admin_user는 필수입니다")
            
            # Langfuse trace 시작 (FR-010)
            langfuse_client = self.langfuse_service.get_client()
            trace_name = "delete_qa_item"
            trace_kwargs = {
                "name": trace_name,
                "input": {
                    "qa_id": request.qa_id,
                    "admin_user": request.admin_user
                },
                "metadata": {
                    "action": "delete",
                    "entity": "qa_item",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Langfuse client가 생성되었으면 trace 사용, 아니면 스킵
            if langfuse_client:
                with langfuse_client.trace(**trace_kwargs) as trace:
                    # ChromaDB에서 삭제
                    self.chromadb_service.delete(request.qa_id)
                    
                    # Langfuse에 기록
                    self.langfuse_service.log_qa_deleted(
                        qa_id=request.qa_id,
                        admin_user=request.admin_user,
                        timestamp=request.timestamp
                    )
                    
                    logger.info(f"Q&A 항목 삭제됨: {request.qa_id} by {request.admin_user}")
                    
                    result = QADeleteResult(
                        success=True,
                        qa_id=request.qa_id,
                        message=f"Q&A 항목이 성공적으로 삭제되었습니다"
                    )
                    
                    # Trace 출력 설정
                    trace.output = {
                        "success": result.success,
                        "message": result.message,
                        "qa_id": result.qa_id
                    }
                    
                    return result
            else:
                # Langfuse가 없으면 기본 동작
                self.chromadb_service.delete(request.qa_id)
                
                self.langfuse_service.log_qa_deleted(
                    qa_id=request.qa_id,
                    admin_user=request.admin_user,
                    timestamp=request.timestamp
                )
                
                logger.info(f"Q&A 항목 삭제됨: {request.qa_id} by {request.admin_user}")
                
                return QADeleteResult(
                    success=True,
                    qa_id=request.qa_id,
                    message=f"Q&A 항목이 성공적으로 삭제되었습니다"
                )
            
            logger.info(f"Q&A 항목 삭제됨: {request.qa_id} by {request.admin_user}")
            
            return QADeleteResult(
                success=True,
                qa_id=request.qa_id,
                message=f"Q&A 항목이 성공적으로 삭제되었습니다"
            )
        
        except Exception as e:
            logger.error(f"Q&A 항목 삭제 실패: {request.qa_id}, 오류: {str(e)}")

            error_reason = str(e)
            if "찾을 수 없습니다" in error_reason:
                user_message = "Q&A 항목을 찾을 수 없습니다"
            elif "network" in error_reason.lower() or "네트워크" in error_reason:
                user_message = "네트워크 오류가 발생했습니다"
            else:
                user_message = "Q&A 항목 삭제 중 오류가 발생했습니다"
            
            return QADeleteResult(
                success=False,
                qa_id=request.qa_id,
                message=user_message,
                error_reason=str(e)
            )


_qa_delete_service_instance: Optional[QADeleteService] = None


def get_qa_delete_service() -> QADeleteService:
    """QADeleteService 싱글톤 팩토리"""
    global _qa_delete_service_instance
    if _qa_delete_service_instance is None:
        _qa_delete_service_instance = QADeleteService()
    return _qa_delete_service_instance
