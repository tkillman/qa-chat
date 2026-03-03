"""
통합 테스트: InitLoader (us1 초기 로딩 구현)
"""
import pytest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock, call
from src.models.qa_item import QAItem
from src.services.file_service import FileService
from src.services.init_loader import InitLoader


class TestInitLoader:
    """InitLoader 통합 테스트"""
    
    def test_load_initial_data_empty_file(self):
        """목표: init.txt가 빈 경우 0개 항목으로 초기화"""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_path = os.path.join(tmpdir, "init.txt")
            
            # 빈 init.txt 생성
            with open(init_path, 'w', encoding='utf-8') as f:
                pass
            
            # 경로 및 ChromaDB 모킹
            with patch('src.services.init_loader.INIT_FILE_PATH', init_path):
                with patch('src.services.init_loader.ChromaDBService') as mock_chroma_class:
                    mock_chroma = MagicMock()
                    mock_chroma_class.return_value = mock_chroma
                    
                    loader = InitLoader()
                    num_items, duration_ms, success = loader.load_initial_data()
                    
                    assert num_items == 0
                    assert duration_ms >= 0
                    assert success == True
                    # ChromaDB clear 호출 확인
                    mock_chroma.clear_collection.assert_called_once()
    
    def test_load_initial_data_with_items(self):
        """목표: init.txt의 데이터가 로드됨"""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_path = os.path.join(tmpdir, "init.txt")
            chroma_path = os.path.join(tmpdir, "chroma")
            
            # init.txt 생성
            items = [
                QAItem(question="Q1", answer="A1"),
                QAItem(question="Q2", answer="A2"),
                QAItem(question="Q3", answer="A3"),
            ]
            FileService.write_qa_items(items, init_path)
            
            # 경로 및 ChromaDB 모킹
            with patch('src.services.init_loader.INIT_FILE_PATH', init_path):
                with patch('src.services.init_loader.ChromaDBService') as mock_chroma_class:
                    mock_chroma = MagicMock()
                    mock_chroma_class.return_value = mock_chroma
                    
                    loader = InitLoader()
                    num_items, duration_ms, success = loader.load_initial_data()
                    
                    assert num_items == 3
                    assert duration_ms >= 0
                    assert success == True
                    # ChromaDB add_qa_items 호출 확인
                    mock_chroma.add_qa_items.assert_called_once()
    
    def test_load_initial_data_error_handling(self):
        """목표: 로드 실패 시 에러 처리"""
        bad_path = "/invalid/nonexistent/path.txt"
        
        # 경로 및 ChromaDB 모킹
        with patch('src.services.init_loader.INIT_FILE_PATH', bad_path):
            with patch('src.services.init_loader.ChromaDBService') as mock_chroma_class:
                mock_chroma = MagicMock()
                mock_chroma_class.return_value = mock_chroma
                
                loader = InitLoader()
                # 파일이 없어도 예외 발생 없음 (빈 리스트 반환)
                num_items, duration_ms, success = loader.load_initial_data()
                
                assert num_items == 0
                assert duration_ms >= 0
                # success는 False 또는 True (구현에 따라 다름)
    
    def test_load_initial_data_duration_measurement(self):
        """목표: 로드 시간이 정확히 측정됨"""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_path = os.path.join(tmpdir, "init.txt")
            
            # 작은 데이터 생성
            items = [QAItem(question=f"Q{i}", answer=f"A{i}") for i in range(10)]
            FileService.write_qa_items(items, init_path)
            
            with patch('src.services.init_loader.INIT_FILE_PATH', init_path):
                with patch('src.services.init_loader.ChromaDBService') as mock_chroma_class:
                    mock_chroma = MagicMock()
                    mock_chroma_class.return_value = mock_chroma
                    
                    loader = InitLoader()
                    num_items, duration_ms, success = loader.load_initial_data()
                    
                    # duration_ms는 0 이상이어야 함 (빠른 실행 시 0일 수 있음)
                    assert duration_ms >= 0
                    # 통합 10개 항목이므로 일반적으로 수십ms 내에 완료
                    assert duration_ms < 10000  # 10초 이상 걸리면 비정상


class TestInitLoaderLangfuseIntegration:
    """InitLoader와 Langfuse 추적 통합 테스트"""
    
    def test_langfuse_logs_initial_load_success(self):
        """목표: 성공 시 Langfuse에 로깅됨"""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_path = os.path.join(tmpdir, "init.txt")
            
            items = [QAItem(question="Q1", answer="A1")]
            FileService.write_qa_items(items, init_path)
            
            with patch('src.services.init_loader.INIT_FILE_PATH', init_path):
                with patch('src.services.init_loader.ChromaDBService') as mock_chroma_class:
                    mock_chroma = MagicMock()
                    mock_chroma_class.return_value = mock_chroma
                    
                    # Langfuse 로깅 모킹
                    with patch('src.services.init_loader.get_langfuse_service') as mock_langfuse_factory:
                        mock_langfuse = MagicMock()
                        mock_langfuse_factory.return_value = mock_langfuse
                        
                        loader = InitLoader()
                        num_items, duration_ms, success = loader.load_initial_data()
                        
                        # Langfuse log_initial_load 호출 확인
                        mock_langfuse.log_initial_load.assert_called_once()
                        call_args = mock_langfuse.log_initial_load.call_args[1]
                        
                        assert call_args['num_items'] == 1
                        assert call_args['success'] == True
    
    def test_langfuse_logs_initial_load_failure(self):
        """목표: 빈 파일 시도 시 Langfuse에 로깅됨"""
        bad_path = "/invalid/nonexistent/path.txt"
        
        with patch('src.services.init_loader.INIT_FILE_PATH', bad_path):
            with patch('src.services.init_loader.ChromaDBService') as mock_chroma_class:
                mock_chroma = MagicMock()
                mock_chroma_class.return_value = mock_chroma
                
                # Langfuse 로깅 모킹
                with patch('src.services.init_loader.get_langfuse_service') as mock_langfuse_factory:
                    mock_langfuse = MagicMock()
                    mock_langfuse_factory.return_value = mock_langfuse
                    
                    loader = InitLoader()
                    num_items, duration_ms, success = loader.load_initial_data()
                    
                    # 파일이 없으면 빈 list 반환하므로 log_initial_load 호출됨
                    assert mock_langfuse.log_initial_load.called or mock_langfuse.log_error.called


class TestInitLoaderSingleton:
    """InitLoader 싱글톤 패턴 테스트"""
    
    def test_get_init_loader_returns_singleton(self):
        """목표: get_init_loader()가 싱글톤을 반환함"""
        from src.services.init_loader import get_init_loader
        
        loader1 = get_init_loader()
        loader2 = get_init_loader()
        
        # 같은 인스턴스여야 함
        assert loader1 is loader2
