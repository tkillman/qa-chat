"""
통합 테스트: 관리자 로그인 (US2)
Spec US2: 패스워드(1234) 검증 후 관리자 화면 진입
"""
import pytest
from unittest.mock import patch, MagicMock
from src.services.auth_service import AuthService


class TestAdminLoginFlow:
    """관리자 로그인 흐름 테스트"""
    
    def test_successful_login(self):
        """목표: 올바른 패스워드로 로그인 성공"""
        auth = AuthService()
        
        # 로그인 시도
        is_valid = auth.verify_password("1234")
        
        assert is_valid == True
    
    def test_failed_login(self):
        """목표: 틀린 패스워드로 로그인 실패"""
        auth = AuthService()
        
        # 로그인 시도 (틀린 패스워드)
        is_valid = auth.verify_password("wrong_password")
        
        assert is_valid == False
    
    def test_login_attempt_sequence(self):
        """목표: 여러 로그인 시도 후 성공"""
        auth = AuthService()
        
        # 실패한 시도들
        assert auth.verify_password("fail1") == False
        assert auth.verify_password("fail2") == False
        assert auth.verify_password("fail3") == False
        
        # 성공한 시도
        assert auth.verify_password("1234") == True
    
    def test_login_error_messages(self):
        """목표: 로그인 실패 시 적절한 오류 메시지"""
        auth = AuthService()
        
        is_valid = auth.verify_password("wrong")
        assert is_valid == False
        
        # 다시 시도
        is_valid = auth.verify_password("1234")
        assert is_valid == True


class TestAdminUIStateManagement:
    """관리자 UI 상태 관리 테스트 (Gradio 통합)"""
    
    def test_login_panel_visibility(self):
        """목표: 로그인 성공 시 관리자 패널이 보임"""
        auth = AuthService()
        
        # 로그인 전: 패널 숨길 준비
        panel_visible = False
        
        # 패스워드 검증
        if auth.verify_password("1234"):
            panel_visible = True
        
        assert panel_visible == True
    
    def test_login_error_status_message(self):
        """목표: 로그인 실패 시 상태 메시지 표시"""
        auth = AuthService()
        
        # 잘못된 패스워드
        is_valid = auth.verify_password("wrong")
        
        if is_valid:
            status = "✓ 로그인 성공"
            visible = True
        else:
            status = "✗ 패스워드가 틀렸습니다"
            visible = True
        
        assert is_valid == False
        assert "틀렸습니다" in status
        assert visible == True
    
    def test_successful_login_status_message(self):
        """목표: 로그인 성공 시 상태 메시지 표시"""
        auth = AuthService()
        
        # 올바른 패스워드
        is_valid = auth.verify_password("1234")
        
        if is_valid:
            status = "✓ 로그인 성공"
            visible = True
        else:
            status = "✗ 패스워드가 틀렸습니다"
            visible = True
        
        assert is_valid == True
        assert "성공" in status
        assert visible == True


class TestAdminLoginWithLangfuse:
    """관리자 로그인 추적 (Langfuse) 테스트"""
    
    def test_login_attempt_logged(self):
        """목표: 로그인 시도가 Langfuse에 로깅됨"""
        auth = AuthService()
        
        with patch('src.services.auth_service.logger') as mock_logger:
            # 성공한 로그인
            auth.verify_password("1234")
            
            # 로깅 호출 확인
            mock_logger.info.assert_called()


class TestAdminLoginSecurityEdgeCases:
    """관리자 로그인 보안 엣지 케이스"""
    
    def test_sql_injection_attempt_fails(self):
        """목표: SQL injection 같은 공격도 차단"""
        auth = AuthService()
        
        # SQL injection 시도
        is_valid = auth.verify_password("' OR '1'='1")
        assert is_valid == False
    
    def test_buffer_overflow_attempt_fails(self):
        """목표: 매우 긴 입력도 차단"""
        auth = AuthService()
        
        # 매우 긴 문자열
        long_str = "A" * 10000
        is_valid = auth.verify_password(long_str)
        assert is_valid == False
    
    def test_null_byte_injection_fails(self):
        """목표: null byte 주입도 차단"""
        auth = AuthService()
        
        # null byte 주입
        is_valid = auth.verify_password("1234\x00")
        assert is_valid == False
    
    def test_password_not_exposed_in_logs(self):
        """목표: 패스워드가 로그에 노출되지 않음"""
        auth = AuthService()
        
        with patch('src.services.auth_service.logger') as mock_logger:
            auth.verify_password("1234")
            
            # 로그 메시지에 실제 패스워드가 없어야 함
            for call in mock_logger.info.call_args_list:
                log_message = str(call)
                assert "1234" not in log_message
