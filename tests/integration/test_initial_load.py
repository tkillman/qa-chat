"""
통합 테스트: User Story 1 - 초기 로딩
목표: app 실행 시 init.txt의 데이터를 ChromaDB에 로드
"""
import pytest
import tempfile
import os
import json
import time
from src.models.qa_item import QAItem
from src.services.file_service import FileService


class TestInitialLoadEmptyFile:
    """US1-T013: init.txt가 없을 때 빈 데이터 초기화"""
    
    def test_no_init_file_returns_empty_list(self):
        """목표: init.txt가 없으면 빈 리스트 반환"""
        items = FileService.read_qa_items("/nonexistent/path/init.txt")
        assert items == []
        assert isinstance(items, list)


class TestInitialLoadWithFile:
    """US1-T014: init.txt가 있을 때 데이터를 로드"""
    
    def test_init_file_loaded_successfully(self):
        """목표: init.txt의 데이터가 로드됨"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            init_path = f.name
        
        try:
            # init.txt 생성
            items = [
                QAItem(question="Python이란?", answer="프로그래밍 언어"),
                QAItem(question="Gradio란?", answer="웹 UI 라이브러리"),
                QAItem(question="ChromaDB란?", answer="벡터 저장소"),
            ]
            FileService.write_qa_items(items, init_path)
            
            # init.txt에서 읽기
            loaded_items = FileService.read_qa_items(init_path)
            assert len(loaded_items) == 3
            assert loaded_items[0].question == "Python이란?"
            assert loaded_items[1].question == "Gradio란?"
            assert loaded_items[2].question == "ChromaDB란?"
        finally:
            os.unlink(init_path)
    
    def test_initial_load_preserves_metadata(self):
        """목표: 메타데이터도 함께 로드됨"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            init_path = f.name
        
        try:
            # 메타데이터 포함 항목
            items = [
                QAItem(
                    question="Question1",
                    answer="Answer1",
                    metadata={"author": "admin", "created": "2024-01-01"}
                ),
            ]
            FileService.write_qa_items(items, init_path)
            
            # 로드 테스트
            loaded_items = FileService.read_qa_items(init_path)
            assert loaded_items[0].metadata == {"author": "admin", "created": "2024-01-01"}
        finally:
            os.unlink(init_path)


class TestInitialLoadErrorHandling:
    """US1-T015: init.txt 형식 오류 시 기본값 처리"""
    
    def test_invalid_json_lines_are_skipped(self):
        """목표: 잘못된 JSON 줄은 건너뛰고 유효한것만 로드"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            init_path = f.name
        
        try:
            # 혼합된 내용 (유효 + 무효)
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write('{"question": "Q1", "answer": "A1"}\n')
                f.write('invalid json line\n')
                f.write('{"question": "Q2", "answer": "A2"}\n')
                f.write('{"question": "Q3", "answer": "A3"}\n')
            
            # 읽기 (유효한 것만 3개)
            items = FileService.read_qa_items(init_path)
            assert len(items) == 3
            assert items[0].question == "Q1"
            assert items[1].question == "Q2"
            assert items[2].question == "Q3"
        finally:
            os.unlink(init_path)
    
    def test_empty_file_does_not_error(self):
        """목표: 빈 파일이나 주석만 있는 파일은 에러 없이 처리"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            init_path = f.name
        
        try:
            # 주석과 빈 줄만 있는 파일
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write("# This is a comment\n")
                f.write("\n")
                f.write("# Another comment\n")
            
            # 에러 없이 빈 리스트 반환
            items = FileService.read_qa_items(init_path)
            assert items == []
        finally:
            os.unlink(init_path)
    
    def test_missing_required_fields_are_handled(self):
        """목표: 필수 필드(question, answer) 누락 시 처리"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            init_path = f.name
        
        try:
            # 필드 누락
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write('{"question": "Q1"}\n')  # answer 없음 → 빈 문자열로 처리
                f.write('{"answer": "A2"}\n')   # question 없음 → 빈 문자열로 처리
                f.write('{"question": "Q3", "answer": "A3"}\n')  # 정상
            
            items = FileService.read_qa_items(init_path)
            # 모두 로드되지만 일부는 빈 필드 포함
            assert len(items) == 3
        finally:
            os.unlink(init_path)
