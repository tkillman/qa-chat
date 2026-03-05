"""
Q&A 항목 삭제 서비스 (Phase 2: Foundational)

헌법 원칙:
- I. 관찰 가능성: Langfuse로 모든 삭제 이벤트 추적
- II. 벡터 인식 데이터 계약: QADeleteRequest/Result로 명시
- III. 사용자 중심 UI: 명확한 오류 메시지 제공
"""
import logging
from typing import Optional
from datetime import datetime

from src.models.qa_delete_models import QADeleteRequest, QADeleteResult

logger = logging.getLogger(__name__)


class QADeleteService:
    """Q&A 항목 삭제를 담당하는 싱글톤 서비스 (data-model.md 참조)
    
    책임:
    - ChromaDB에서 ID 기반으로 Q&A 항목 삭제
    - 오류 처리 및 메시지 매핑
    - Langfuse 추적 통합 (FR-010)
    
    동시성 전략: Optimistic (first-wins)
    - 첫 번째 요청: 성공
    - 두 번째 요청 (같은 항목): not_found 오류
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
        self._initialized = True
    
    def _ensure_dependencies(self):
        """의존성 가져오기"""
        if self.chromadb_service is None:
            from src.services.chromadb_service import ChromaDBService
            self.chromadb_service = ChromaDBService()
        
        if self.langfuse_service is None:
            from src.services.langfuse_service import LangfuseService
            self.langfuse_service = LangfuseService()
    
    def delete_qa_item(self, request: QADeleteRequest) -> QADeleteResult:
        """Q&A 항목 삭제 (contracts/delete-request.md 참조)
        
        Args:
            request: 삭제 요청 정보 (QADeleteRequest)
        
        Returns:
            QADeleteResult: 삭제 작업 결과 (contracts/delete-response.md 참조)
        
        Process:
            1. 요청 유효성 검사
            2. Langfuse trace 시작 (FR-010)
            3. ChromaDB에서 삭제
            4. Langfuse에 결과 기록
            5. 성공/실패 응답 반환
        
        Error Handling (data-model.md 오류 분류):
            - not_found: 항목 없음 (재시도 불가)
            - db_connection_error: DB 연결 실패 (재시도 가능)
            - db_operation_error: DB 작업 실패 (재시도 가능)
            - network_error: 네트워크 오류 (재시도 가능)
            - timeout: 타임아웃 (재시도 가능)
            - unknown_error: 예기치 않은 오류 (재시도 가능)
        """
        self._ensure_dependencies()
        
        try:
            # 1️⃣ 요청 유효성 검사
            request.validate()
            
            logger.info(f"❌ 삭제 요청 시작: qa_id={request.qa_id}, admin_user={request.admin_user}")
            
            # 2️⃣ Langfuse trace 시작 (FR-010)
            langfuse_client = self.langfuse_service.get_client()
            
            if langfuse_client:
                trace_name = "delete_qa_item"
                trace_input = {
                    "qa_id": request.qa_id,
                    "admin_user": request.admin_user,
                    "timestamp": request.timestamp.isoformat()
                }
                
                with langfuse_client.trace(
                    name=trace_name,
                    input=trace_input,
                    metadata={
                        "action": "delete",
                        "entity": "qa_item",
                        "source": "admin_ui"
                    }
                ) as trace:
                    # 3️⃣ ChromaDB에서 삭제
                    self.chromadb_service.delete(request.qa_id)
                    
                    # 4️⃣ Langfuse에 결과 기록
                    result = QADeleteResult(
                        success=True,
                        qa_id=request.qa_id,
                        message="✓ 삭제되었습니다"
                    )
                    
                    trace.output = {
                        "success": result.success,
                        "message": result.message,
                        "qa_id": result.qa_id,
                        "timestamp": result.timestamp.isoformat()
                    }
                    
                    logger.info(f"✅ Q&A 항목 삭제 성공: {request.qa_id}")
                    return result
            else:
                # Langfuse 미형성화 시 기본 동작
                logger.warning("Langfuse not initialized, skipping trace")
                self.chromadb_service.delete(request.qa_id)
                
                result = QADeleteResult(
                    success=True,
                    qa_id=request.qa_id,
                    message="✓ 삭제되었습니다"
                )
                
                logger.info(f"✅ Q&A 항목 삭제 성공: {request.qa_id}")
                return result
        
        except ValueError as e:
            # 입력 검증 오류
            logger.warning(f"❌ 검증 오류: {str(e)}")
            return QADeleteResult(
                success=False,
                qa_id=request.qa_id,
                message=str(e),
                error_reason="unknown_error"
            )
        
        except Exception as e:
            # 실행 중 오류
            logger.error(f"❌ 삭제 실패: {str(e)}", exc_info=True)
            
            # 오류 원인 분류
            error_reason, user_message = self._classify_error(str(e), request.qa_id)
            
            return QADeleteResult(
                success=False,
                qa_id=request.qa_id,
                message=user_message,
                error_reason=error_reason
            )
    
    def _classify_error(self, error_msg: str, qa_id: str) -> tuple[str, str]:
        """오류를 분류하고 사용자 메시지 생성 (data-model.md 오류 분류 코드)
        
        Args:
            error_msg: 원본 오류 메시지
            qa_id: Q&A ID (로그용)
        
        Returns:
            (error_reason: str, user_message: str): 오류 분류 코드와 사용자 메시지
        """
        error_lower = error_msg.lower()
        
        # 항목 없음
        if "notfound" in error_lower or "존재하지 않음" in error_lower or "찾을 수 없" in error_lower:
            return "not_found", "항목을 찾을 수 없습니다"
        
        # DB 연결 오류
        if "connection" in error_lower or "연결" in error_lower:
            return "db_connection_error", "데이터베이스 연결 오류"
        
        # 네트워크 오류
        if "network" in error_lower or "네트워크" in error_lower or "timeout" in error_lower:
            return "network_error", "네트워크 오류가 발생했습니다"
        
        # DB 작업 오류
        if "database" in error_lower or "chromadb" in error_lower:
            return "db_operation_error", "데이터베이스 작업 실패"
        
        # 기타 오류
        return "unknown_error", "알 수 없는 오류가 발생했습니다"


_qa_delete_service_instance: Optional[QADeleteService] = None


def get_qa_delete_service() -> QADeleteService:
    """QADeleteService 싱글톤 팩토리 함수
    
    Returns:
        QADeleteService: 싱글톤 인스턴스
    """
    global _qa_delete_service_instance
    if _qa_delete_service_instance is None:
        _qa_delete_service_instance = QADeleteService()
    return _qa_delete_service_instance
