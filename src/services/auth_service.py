"""
인증 서비스 - 관리자 패스워드 검증
Spec US2: 패스워드(1234) 검증 후 관리자 화면 진입
Spec FR-002: 환경변수 ADMIN_PASSWORD 사용 (기본값: 1234)
"""
import logging
from typing import Optional
from src.config import ADMIN_PASSWORD

logger = logging.getLogger(__name__)


class AuthService:
    """관리자 인증 서비스"""
    
    def __init__(self, password: Optional[str] = None):
        """인증 서비스 초기화
        
        Args:
            password: 관리자 패스워드 (None이면 config.ADMIN_PASSWORD 사용)
        """
        self.password = password if password is not None else ADMIN_PASSWORD
    
    def verify_password(self, input_password: Optional[str]) -> bool:
        """패스워드 검증 (US2 FR-002)
        
        Args:
            input_password: 사용자가 입력한 패스워드
            
        Returns:
            검증 성공 여부
        """
        # None 또는 빈 문자열 체크
        if not input_password:
            logger.warning("Empty password provided")
            return False
        
        # 정확한 일치 검증 (대소문자 민감, 공백 무시 안 함)
        result = input_password == self.password
        
        if not result:
            logger.warning(f"Password verification failed (length: {len(input_password)})")
        else:
            logger.info("Password verification successful")
        
        return result
    
    def get_password_requirements(self) -> dict:
        """패스워드 요구사항 반환
        
        Returns:
            패스워드 요구사항 정보
        """
        return {
            "length": len(self.password),
            "case_sensitive": True,
            "allow_special_chars": True,
            "allow_unicode": True,
        }


# 글로벌 인스턴스
_auth_service: Optional[AuthService] = None


def get_auth_service(password: Optional[str] = None) -> AuthService:
    """AuthService 인스턴스 반환
    
    Args:
        password: 커스텀 패스워드 (기본: None, ADMIN_PASSWORD 사용)
        
    Returns:
        AuthService 인스턴스
    """
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService(password)
    return _auth_service
