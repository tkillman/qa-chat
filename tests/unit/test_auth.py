"""
단위 테스트: 인증 서비스 (관리자 패스워드 검증)
Spec US2: 패스워드(1234) 검증 후 관리자 화면 진입
Spec FR-002: 환경변수 ADMIN_PASSWORD (기본값: 1234)
"""
import pytest
from src.services.auth_service import AuthService
from src.config import ADMIN_PASSWORD
from unittest.mock import patch


class TestAuthService:
    """인증 서비스 (패스워드) 테스트"""
    
    def test_correct_password_passes(self):
        """목표: 올바른 패스워드가 검증됨"""
        auth = AuthService()
        
        # 기본 패스워드 (1234)
        result = auth.verify_password("1234")
        assert result == True
    
    def test_incorrect_password_fails(self):
        """목표: 틀린 패스워드는 검증 실패"""
        auth = AuthService()
        
        result = auth.verify_password("wrong")
        assert result == False
    
    def test_empty_password_fails(self):
        """목표: 빈 패스워드는 검증 실패"""
        auth = AuthService()
        
        result = auth.verify_password("")
        assert result == False
    
    def test_none_password_fails(self):
        """목표: None 패스워드는 검증 실패"""
        auth = AuthService()
        
        result = auth.verify_password(None)
        assert result == False
    
    def test_case_sensitive_password(self):
        """목표: 패스워드는 정확한 일치 필요"""
        auth = AuthService(password="TestPass")
        
        # 대문자/소문자 다른 경우 실패
        result = auth.verify_password("testpass")
        assert result == False
        
        # 정확한 대소문자
        result = auth.verify_password("TestPass")
        assert result == True

    
    def test_password_with_whitespace_fails(self):
        """목표: 공백이 포함된 패스워드는 실패"""
        auth = AuthService()
        
        result = auth.verify_password(" 1234 ")
        assert result == False
    
    def test_custom_password_from_config(self):
        """목표: 설정된 패스워드로 검증"""
        # 기본 설정은 1234
        assert ADMIN_PASSWORD == "1234"
        
        auth = AuthService()
        result = auth.verify_password(ADMIN_PASSWORD)
        assert result == True
    
    def test_custom_password_override(self):
        """목표: 커스텀 패스워드 설정 가능"""
        auth = AuthService(password="custom_pass")
        
        # 기본값이 아닌 커스텀 패스워드로 검증
        result = auth.verify_password("custom_pass")
        assert result == True
        
        # 기본값은 실패
        result = auth.verify_password("1234")
        assert result == False


class TestAuthServiceEdgeCases:
    """인증 서비스 엣지 케이스"""
    
    def test_password_length_validation(self):
        """목표: 패스워드 길이 검증"""
        auth = AuthService()
        
        # 너무 짧음
        assert auth.verify_password("12") == False
        
        # 정확한 길이
        assert auth.verify_password("1234") == True
        
        # 너무 김
        assert auth.verify_password("1234extra") == False
    
    def test_special_characters_in_password(self):
        """목표: 특수문자가 포함된 패스워드 처리"""
        auth = AuthService(password="pass@123!")
        
        result = auth.verify_password("pass@123!")
        assert result == True
        
        # 특수문자 없으면 실패
        result = auth.verify_password("pass123")
        assert result == False
    
    def test_unicode_password(self):
        """목표: 유니코드 패스워드 처리"""
        auth = AuthService(password="암호1234")
        
        result = auth.verify_password("암호1234")
        assert result == True
        
        result = auth.verify_password("1234")
        assert result == False
    
    def test_repeated_failed_attempts(self):
        """목표: 여러 번 실패해도 작동"""
        auth = AuthService()
        
        # 여러 번 실패
        for _ in range(5):
            result = auth.verify_password("wrong")
            assert result == False
        
        # 그 후 정확한 패스워드
        result = auth.verify_password("1234")
        assert result == True
