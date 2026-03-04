"""
Q&A 항목 삭제 기능 - 데이터 모델
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class QADeleteRequest:
    """삭제 요청을 나타내는 데이터 구조
    
    Attributes:
        qa_id: 삭제할 Q&A 항목의 고유 ID (Hash ID 형식)
        admin_user: 삭제 요청한 관리자 사용자명
        timestamp: 삭제 요청 시간
    """
    qa_id: str
    admin_user: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QADeleteResult:
    """삭제 작업 결과를 나타내는 데이터 구조
    
    Attributes:
        success: 삭제 성공 여부
        qa_id: 삭제된 Q&A 항목 ID
        message: 결과 메시지
        error_reason: 실패 시 오류 원인 (선택사항)
    """
    success: bool
    qa_id: str
    message: str
    error_reason: Optional[str] = None

    def __post_init__(self):
        """유효성 검사"""
        if not self.qa_id:
            raise ValueError("qa_id는 빈 값이 될 수 없습니다")
        if not self.message:
            raise ValueError("message는 빈 값이 될 수 없습니다")
        if not self.success and not self.error_reason:
            raise ValueError("success가 False인 경우 error_reason이 필수입니다")
