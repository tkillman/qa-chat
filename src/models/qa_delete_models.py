"""
Q&A 항목 삭제 기능 - 데이터 모델 (Phase 2: Foundational)

헌법 원칙 II: 벡터 인식 데이터 계약
- 모든 모델은 검증 규칙과 타입 안전성을 제공합니다
"""
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional


@dataclass
class QADeleteRequest:
    """삭제 요청을 나타내는 데이터 구조 (data-model.md 참조)
    
    Attributes:
        qa_id: 삭제할 Q&A 항목의 고유 ID (Hash ID 형식, QAItem.get_hash_key())
        admin_user: 삭제 요청한 관리자 사용자명 (감사 추적용)
        timestamp: 삭제 요청 시간 (UTC)
    
    Example:
        >>> req = QADeleteRequest(
        ...     qa_id="abc123def456",
        ...     admin_user="admin"
        ... )
        >>> req.validate()
        True
    """
    qa_id: str
    admin_user: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def validate(self) -> bool:
        """요청 유효성 검증 (data-model.md 검증 규칙)
        
        Returns:
            bool: 유효하면 True
            
        Raises:
            ValueError: 필수 필드가 비어있으면 예외
        """
        # Rule 1: qa_id 필수
        if not self.qa_id or not self.qa_id.strip():
            raise ValueError("qa_id는 비워둘 수 없습니다")
        
        # Rule 2: admin_user 필수
        if not self.admin_user or not self.admin_user.strip():
            raise ValueError("admin_user는 비워둘 수 없습니다")
        
        # Rule 3: qa_id는 질문 문자열 기반 ID도 허용
        # (현재 시스템의 get_hash_key()가 정규화된 질문 문자열을 반환하므로
        #  공백/특수문자를 포함할 수 있어 과도한 정규식 제한을 두지 않음)
        if len(self.qa_id.strip()) > 500:
            raise ValueError("qa_id 길이가 너무 깁니다")
        
        # Rule 4: admin_user 길이 제한
        if len(self.admin_user) > 50:
            raise ValueError("admin_user는 50자 이하여야 합니다")
        
        return True


@dataclass
class QADeleteResult:
    """삭제 작업 결과를 나타내는 데이터 구조 (data-model.md 참조)
    
    Attributes:
        success: 삭제 성공 여부
        qa_id: 삭제된 Q&A 항목 ID (요청과 동일)
        message: 사용자 친화적 메시지 (UI에 표시)
        error_reason: 실패 사유 (내부 분류 코드, 개발자용)
        timestamp: 완료 시각 (UTC, 성능 측정용)
    
    Example:
        >>> # 성공
        >>> result = QADeleteResult(
        ...     success=True,
        ...     qa_id="abc123def456",
        ...     message="✓ 삭제되었습니다"
        ... )
        
        >>> # 실패
        >>> result = QADeleteResult(
        ...     success=False,
        ...     qa_id="xyz789",
        ...     message="항목을 찾을 수 없습니다",
        ...     error_reason="not_found"
        ... )
    """
    success: bool
    qa_id: str
    message: str
    error_reason: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    # 허용된 error_reason 값 (data-model.md: 오류 분류 코드)
    VALID_ERROR_REASONS = {
        "not_found", "permission_denied", "db_connection_error",
        "db_operation_error", "network_error", "timeout", "unknown_error"
    }

    def __post_init__(self):
        """유효성 검사 (data-model.md 검증 규칙)"""
        # Rule 1: qa_id 필수
        if not self.qa_id:
            raise ValueError("qa_id는 빈 값이 될 수 없습니다")
        
        # Rule 2: message 필수
        if not self.message or not self.message.strip():
            raise ValueError("message는 빈 값이 될 수 없습니다")
        
        # Rule 3: success=False이면 error_reason 필수
        if not self.success and not self.error_reason:
            raise ValueError("success가 False인 경우 error_reason이 필수입니다")
        
        # Rule 4: success=True이면 error_reason은 None
        if self.success and self.error_reason:
            raise ValueError("success가 True인 경우 error_reason은 None이어야 합니다")
        
        # Rule 5: error_reason이 유효한 값인지 확인
        if self.error_reason and self.error_reason not in self.VALID_ERROR_REASONS:
            raise ValueError(f"error_reason은 {self.VALID_ERROR_REASONS} 중 하나여야 합니다")
    
    def is_not_found(self) -> bool:
        """항목을 찾을 수 없는 오류인지 확인"""
        return not self.success and self.error_reason == "not_found"
    
    def is_retriable(self) -> bool:
        """재시도 가능한 오류인지 확인"""
        return not self.success and self.error_reason in [
            "db_connection_error",
            "db_operation_error",
            "network_error",
            "timeout",
        ]
