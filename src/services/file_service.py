"""
파일 시스템 관련 서비스 - init.txt 읽기/쓰기
"""
import os
import json
from pathlib import Path
from typing import List, Optional
from src.models.qa_item import QAItem
from src.config import INIT_FILE_PATH
import logging

logger = logging.getLogger(__name__)


class FileService:
    """init.txt 파일 관리 서비스"""
    
    @staticmethod
    def read_qa_items(file_path: str = INIT_FILE_PATH) -> List[QAItem]:
        """init.txt에서 Q&A 항목 읽기
        
        Args:
            file_path: 읽을 파일 경로 (기본: config.INIT_FILE_PATH)
            
        Returns:
            QAItem 리스트
            
        Raises:
            FileNotFoundError: 파일이 없을 경우
            ValueError: JSON 형식 오류 있을 경우
        """
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return []
        
        items = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    # 빈 줄이나 주석은 무시
                    if not line or line.startswith('#'):
                        continue
                    
                    try:
                        item = QAItem.from_json_line(line)
                        items.append(item)
                    except ValueError as e:
                        logger.warning(f"Skipping malformed JSONL line {line_num}: {e}")
                        continue
            
            logger.info(f"Successfully read {len(items)} QA items from {file_path}")
            return items
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    @staticmethod
    def write_qa_items(items: List[QAItem], file_path: str = INIT_FILE_PATH) -> None:
        """Q&A 항목을 init.txt에 작성
        
        Args:
            items: 작성할 QAItem 리스트
            file_path: 작성할 파일 경로 (기본: config.INIT_FILE_PATH)
            
        Raises:
            IOError: 파일 작성 실패 시
        """
        # 디렉토리 생성
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for item in items:
                    f.write(item.to_json_line() + '\n')
            
            logger.info(f"Successfully wrote {len(items)} QA items to {file_path}")
            
        except Exception as e:
            logger.error(f"Error writing to file {file_path}: {e}")
            raise
    
    @staticmethod
    def append_qa_item(item: QAItem, file_path: str = INIT_FILE_PATH) -> None:
        """Q&A 항목을 init.txt에 추가
        
        Args:
            item: 추가할 QAItem
            file_path: 파일 경로 (기본: config.INIT_FILE_PATH)
            
        Raises:
            IOError: 파일 작성 실패 시
        """
        # 디렉토리 생성
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(item.to_json_line() + '\n')
            
            logger.info(f"Appended QA item to {file_path}")
            
        except Exception as e:
            logger.error(f"Error appending to file {file_path}: {e}")
            raise
    
    @staticmethod
    def delete_qa_item(question: str, file_path: str = INIT_FILE_PATH) -> bool:
        """특정 질문을 제거하고 파일 다시 쓰기
        
        Args:
            question: 삭제할 질문
            file_path: 파일 경로 (기본: config.INIT_FILE_PATH)
            
        Returns:
            삭제 성공 여부
        """
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return False
        
        try:
            items = FileService.read_qa_items(file_path)
            target_key = question.strip().lower()
            
            # 일치하는 항목 필터링
            filtered_items = [
                item for item in items
                if item.get_hash_key() != target_key
            ]
            
            if len(filtered_items) < len(items):
                FileService.write_qa_items(filtered_items, file_path)
                logger.info(f"Deleted QA item with question: {question}")
                return True
            else:
                logger.warning(f"Question not found: {question}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting QA item: {e}")
            raise
    
    @staticmethod
    def update_or_insert_qa_item(item: QAItem, file_path: str = INIT_FILE_PATH) -> None:
        """중복된 질문이면 덮어쓰고, 없으면 추가 (Spec FR-008)
        
        Args:
            item: 추가/업데이트할 QAItem
            file_path: 파일 경로 (기본: config.INIT_FILE_PATH)
        """
        if not os.path.exists(file_path):
            FileService.append_qa_item(item, file_path)
            return
        
        try:
            items = FileService.read_qa_items(file_path)
            target_key = item.get_hash_key()
            
            # 기존 항목 찾기
            updated = False
            for i, existing in enumerate(items):
                if existing.get_hash_key() == target_key:
                    items[i] = item
                    updated = True
                    break
            
            # 없으면 추가
            if not updated:
                items.append(item)
            
            FileService.write_qa_items(items, file_path)
            logger.info(f"Updated or inserted QA item: {item.question}")
            
        except Exception as e:
            logger.error(f"Error updating/inserting QA item: {e}")
            raise
