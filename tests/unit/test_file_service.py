"""
Unit 테스트: FileService (init.txt 읽기/쓰기)
"""
import pytest
import json
import tempfile
import os
from src.models.qa_item import QAItem
from src.services.file_service import FileService


class TestFileServiceRead:
    """init.txt 읽기 테스트"""
    
    def test_read_empty_file(self):
        """목표: 빈 파일에서 빈 리스트 반환"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("")
            temp_path = f.name
        
        try:
            result = FileService.read_qa_items(temp_path)
            assert result == []
        finally:
            os.unlink(temp_path)
    
    def test_read_single_item(self):
        """목표: 한 줄의 JSON을 읽어 QAItem으로 변환"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            item_data = {"question": "Python이란?", "answer": "프로그래밍 언어"}
            f.write(json.dumps(item_data, ensure_ascii=False) + "\n")
            temp_path = f.name
        
        try:
            result = FileService.read_qa_items(temp_path)
            assert len(result) == 1
            assert result[0].question == "Python이란?"
            assert result[0].answer == "프로그래밍 언어"
        finally:
            os.unlink(temp_path)
    
    def test_read_multiple_items(self):
        """목표: 여러 개의 Q&A 항목 읽기"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            items = [
                {"question": "Q1", "answer": "A1"},
                {"question": "Q2", "answer": "A2", "metadata": {"author": "admin"}},
            ]
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
            temp_path = f.name
        
        try:
            result = FileService.read_qa_items(temp_path)
            assert len(result) == 2
            assert result[0].question == "Q1"
            assert result[1].metadata == {"author": "admin"}
        finally:
            os.unlink(temp_path)
    
    def test_read_skip_empty_lines_and_comments(self):
        """목표: 빈 줄과 주석(#)은 무시"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("# 이것은 주석입니다\n")
            f.write("\n")  # 빈 줄
            f.write(json.dumps({"question": "Q1", "answer": "A1"}, ensure_ascii=False) + "\n")
            f.write("   \n")  # 공백만 있는 줄
            temp_path = f.name
        
        try:
            result = FileService.read_qa_items(temp_path)
            assert len(result) == 1
            assert result[0].question == "Q1"
        finally:
            os.unlink(temp_path)
    
    def test_read_file_not_found(self):
        """목표: 파일이 없으면 빈 리스트 반환"""
        result = FileService.read_qa_items("/nonexistent/path/file.txt")
        assert result == []
    
    def test_read_invalid_json_line_is_logged(self, caplog):
        """목표: 잘못된 JSON 줄은 건너뛰고 로그 기록"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write('{"question": "Q1", "answer": "A1"}\n')
            f.write('invalid json line\n')
            f.write('{"question": "Q2", "answer": "A2"}\n')
            temp_path = f.name
        
        try:
            result = FileService.read_qa_items(temp_path)
            assert len(result) == 2  # 유효한 것만 2개
            assert result[0].question == "Q1"
            assert result[1].question == "Q2"
        finally:
            os.unlink(temp_path)


class TestFileServiceWrite:
    """init.txt 작성 테스트"""
    
    def test_write_single_item(self):
        """목표: QAItem을 JSON 줄로 작성"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name
        
        try:
            items = [QAItem(question="Q1", answer="A1")]
            FileService.write_qa_items(items, temp_path)
            
            result = FileService.read_qa_items(temp_path)
            assert len(result) == 1
            assert result[0].question == "Q1"
        finally:
            os.unlink(temp_path)
    
    def test_write_creates_directory(self):
        """목표: 디렉토리가 없으면 생성"""
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, "subdir", "qa_items.txt")
        
        try:
            items = [QAItem(question="Q1", answer="A1")]
            FileService.write_qa_items(items, temp_path)
            
            assert os.path.exists(temp_path)
            result = FileService.read_qa_items(temp_path)
            assert len(result) == 1
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_write_overwrites_existing_file(self):
        """목표: 기존 파일을 덮어쓰기"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name
        
        try:
            # 첫 번째 쓰기
            FileService.write_qa_items([QAItem(question="Old", answer="Data")], temp_path)
            
            # 두 번째 쓰기 (덮어쓰기)
            FileService.write_qa_items([
                QAItem(question="New1", answer="Data1"),
                QAItem(question="New2", answer="Data2")
            ], temp_path)
            
            result = FileService.read_qa_items(temp_path)
            assert len(result) == 2
            assert result[0].question == "New1"
        finally:
            os.unlink(temp_path)


class TestFileServiceUpdateOrInsert:
    """중복 질문 처리 (FR-008) 테스트"""
    
    def test_update_existing_question(self):
        """목표: 기존 질문이면 덮어쓰기"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write(json.dumps({"question": "Python", "answer": "Old Answer"}, ensure_ascii=False) + "\n")
            temp_path = f.name
        
        try:
            new_item = QAItem(question="Python", answer="New Answer")
            FileService.update_or_insert_qa_item(new_item, temp_path)
            
            result = FileService.read_qa_items(temp_path)
            assert len(result) == 1  # 기존 것을 덮어씀
            assert result[0].answer == "New Answer"
        finally:
            os.unlink(temp_path)
    
    def test_insert_new_question(self):
        """목표: 새 질문이면 추가"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write(json.dumps({"question": "Python", "answer": "Answer1"}, ensure_ascii=False) + "\n")
            temp_path = f.name
        
        try:
            new_item = QAItem(question="Java", answer="Answer2")
            FileService.update_or_insert_qa_item(new_item, temp_path)
            
            result = FileService.read_qa_items(temp_path)
            assert len(result) == 2
            assert result[1].question == "Java"
        finally:
            os.unlink(temp_path)
    
    def test_update_preserves_other_items(self):
        """목표: 업데이트 시 다른 항목은 유지"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write(json.dumps({"question": "Q1", "answer": "A1"}, ensure_ascii=False) + "\n")
            f.write(json.dumps({"question": "Q2", "answer": "A2"}, ensure_ascii=False) + "\n")
            f.write(json.dumps({"question": "Q3", "answer": "A3"}, ensure_ascii=False) + "\n")
            temp_path = f.name
        
        try:
            updated = QAItem(question="Q2", answer="Updated A2")
            FileService.update_or_insert_qa_item(updated, temp_path)
            
            result = FileService.read_qa_items(temp_path)
            assert len(result) == 3
            assert result[0].question == "Q1"
            assert result[1].answer == "Updated A2"
            assert result[2].question == "Q3"
        finally:
            os.unlink(temp_path)
