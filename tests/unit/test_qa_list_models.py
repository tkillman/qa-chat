"""테스트: QA 목록 조회용 데이터 모델

이 모듈은 QAListItem, PaginationState, ListViewState 모델의 동작을 검증합니다.
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from models.qa_list_models import QAListItem, PaginationState, ListViewState


class TestQAListItem:
    """QAListItem 모델 테스트"""
    
    def test_qa_list_item_creation(self):
        """정상적인 QAListItem 생성 테스트"""
        item = QAListItem(
            question="What is Python?",
            answer="Python is a programming language",
            id="hash123",
            created_at="2026-03-05T10:00:00"
        )
        
        assert item.question == "What is Python?"
        assert item.answer == "Python is a programming language"
        assert item.id == "hash123"
        assert item.created_at == "2026-03-05T10:00:00"
        assert item.metadata is None
    
    def test_qa_list_item_with_metadata(self):
        """메타데이터를 포함한 QAListItem 생성 테스트"""
        metadata = {"source": "user1", "category": "python"}
        item = QAListItem(
            question="What is Python?",
            answer="Python is a programming language",
            id="hash123",
            created_at="2026-03-05T10:00:00",
            metadata=metadata
        )
        
        assert item.metadata == metadata
        assert item.metadata["source"] == "user1"
    
    def test_qa_list_item_empty_question_raises_error(self):
        """빈 질문으로 생성 시 오류 발생 테스트"""
        with pytest.raises(ValueError, match="Question cannot be empty"):
            QAListItem(
                question="",
                answer="Some answer",
                id="hash123",
                created_at="2026-03-05T10:00:00"
            )
    
    def test_qa_list_item_whitespace_question_raises_error(self):
        """공백만 있는 질문으로 생성 시 오류 발생 테스트"""
        with pytest.raises(ValueError, match="Question cannot be empty"):
            QAListItem(
                question="   ",
                answer="Some answer",
                id="hash123",
                created_at="2026-03-05T10:00:00"
            )
    
    def test_qa_list_item_empty_answer_raises_error(self):
        """빈 답변으로 생성 시 오류 발생 테스트"""
        with pytest.raises(ValueError, match="Answer cannot be empty"):
            QAListItem(
                question="What is Python?",
                answer="",
                id="hash123",
                created_at="2026-03-05T10:00:00"
            )
    
    def test_qa_list_item_empty_id_raises_error(self):
        """빈 ID로 생성 시 오류 발생 테스트"""
        with pytest.raises(ValueError, match="ID cannot be empty"):
            QAListItem(
                question="What is Python?",
                answer="Some answer",
                id="",
                created_at="2026-03-05T10:00:00"
            )
    
    def test_qa_list_item_empty_created_at_raises_error(self):
        """빈 created_at으로 생성 시 오류 발생 테스트"""
        with pytest.raises(ValueError, match="created_at cannot be empty"):
            QAListItem(
                question="What is Python?",
                answer="Some answer",
                id="hash123",
                created_at=""
            )
    
    def test_qa_list_item_to_dict(self):
        """QAListItem을 딕셔너리로 변환 테스트"""
        metadata = {"source": "user1"}
        item = QAListItem(
            question="What is Python?",
            answer="Python is a programming language",
            id="hash123",
            created_at="2026-03-05T10:00:00",
            metadata=metadata
        )
        
        result = item.to_dict()
        
        assert result["question"] == "What is Python?"
        assert result["answer"] == "Python is a programming language"
        assert result["id"] == "hash123"
        assert result["created_at"] == "2026-03-05T10:00:00"
        assert result["metadata"] == metadata
    
    def test_qa_list_item_from_chromadb_result(self):
        """ChromaDB 결과에서 QAListItem 생성 테스트"""
        doc = "What is Python?"
        metadata = {
            "answer": "Python is a programming language",
            "created_at": "2026-03-05T10:00:00"
        }
        id = "hash123"
        
        item = QAListItem.from_chromadb_result(doc, metadata, id)
        
        assert item.question == "What is Python?"
        assert item.answer == "Python is a programming language"
        assert item.id == "hash123"
        assert item.created_at == "2026-03-05T10:00:00"
    
    def test_qa_list_item_from_chromadb_result_missing_created_at(self):
        """ChromaDB 결과에서 created_at 누락 시 기본값 사용 테스트"""
        doc = "What is Python?"
        metadata = {"answer": "Python is a programming language"}
        id = "hash123"
        
        item = QAListItem.from_chromadb_result(doc, metadata, id)
        
        assert item.created_at == "2000-01-01T00:00:00"


class TestPaginationState:
    """PaginationState 모델 테스트"""
    
    def test_pagination_state_creation(self):
        """정상적인 PaginationState 생성 테스트"""
        pagination = PaginationState(
            current_page=1,
            items_per_page=10,
            total_items=37
        )
        
        assert pagination.current_page == 1
        assert pagination.items_per_page == 10
        assert pagination.total_items == 37
        assert pagination.total_pages == 4  # ceil(37/10)
    
    def test_pagination_state_default_values(self):
        """기본값으로 PaginationState 생성 테스트"""
        pagination = PaginationState()
        
        assert pagination.current_page == 1
        assert pagination.items_per_page == 10
        assert pagination.total_items == 0
        assert pagination.total_pages == 1
    
    def test_pagination_state_invalid_items_per_page(self):
        """잘못된 items_per_page로 생성 시 오류 발생 테스트"""
        with pytest.raises(ValueError, match="items_per_page must be"):
            PaginationState(
                current_page=1,
                items_per_page=15,  # 허용된 값 아님 (10, 20, 50만 가능)
                total_items=37
            )
    
    def test_pagination_state_negative_current_page_corrected(self):
        """음수 current_page 자동 보정 테스트"""
        pagination = PaginationState(
            current_page=-1,
            items_per_page=10,
            total_items=37
        )
        
        assert pagination.current_page == 1
    
    def test_pagination_state_current_page_beyond_total_corrected(self):
        """total_pages를 벗어난 current_page 자동 보정 테스트"""
        pagination = PaginationState(
            current_page=10,  # 총 4페이지인데 10페이지 요청
            items_per_page=10,
            total_items=37
        )
        
        assert pagination.current_page == 4
    
    def test_pagination_state_total_pages_calculation(self):
        """total_pages 자동 계산 테스트"""
        test_cases = [
            (0, 10, 1),    # 0개 항목 → 1페이지
            (10, 10, 1),   # 10개 항목 → 1페이지
            (11, 10, 2),   # 11개 항목 → 2페이지
            (37, 10, 4),   # 37개 항목 → 4페이지
            (100, 20, 5),  # 100개 항목 20개/페이지 → 5페이지
        ]
        
        for total_items, items_per_page, expected_pages in test_cases:
            pagination = PaginationState(
                items_per_page=items_per_page,
                total_items=total_items
            )
            assert pagination.total_pages == expected_pages
    
    def test_has_prev_first_page(self):
        """첫 페이지에서 has_prev() 반환값 테스트"""
        pagination = PaginationState(
            current_page=1,
            items_per_page=10,
            total_items=37
        )
        
        assert pagination.has_prev() is False
    
    def test_has_prev_other_pages(self):
        """다른 페이지에서 has_prev() 반환값 테스트"""
        pagination = PaginationState(
            current_page=2,
            items_per_page=10,
            total_items=37
        )
        
        assert pagination.has_prev() is True
    
    def test_has_next_last_page(self):
        """마지막 페이지에서 has_next() 반환값 테스트"""
        pagination = PaginationState(
            current_page=4,
            items_per_page=10,
            total_items=37
        )
        
        assert pagination.has_next() is False
    
    def test_has_next_other_pages(self):
        """다른 페이지에서 has_next() 반환값 테스트"""
        pagination = PaginationState(
            current_page=1,
            items_per_page=10,
            total_items=37
        )
        
        assert pagination.has_next() is True
    
    def test_get_offset(self):
        """get_offset() 계산 테스트"""
        test_cases = [
            (1, 10, 0),    # 페이지 1 → offset 0
            (2, 10, 10),   # 페이지 2 → offset 10
            (3, 10, 20),   # 페이지 3 → offset 20
            (1, 20, 0),    # 페이지 1, 20개/페이지 → offset 0
            (2, 20, 20),   # 페이지 2, 20개/페이지 → offset 20
        ]
        
        for current_page, items_per_page, expected_offset in test_cases:
            pagination = PaginationState(
                current_page=current_page,
                items_per_page=items_per_page,
                total_items=100
            )
            assert pagination.get_offset() == expected_offset
    
    def test_get_page_info_text(self):
        """get_page_info_text() 반환값 테스트"""
        pagination = PaginationState(
            current_page=2,
            items_per_page=10,
            total_items=37
        )
        
        assert pagination.get_page_info_text() == "페이지 2/4"
    
    def test_get_total_items_text(self):
        """get_total_items_text() 반환값 테스트"""
        pagination = PaginationState(
            total_items=37
        )
        
        assert pagination.get_total_items_text() == "총 37개의 항목"
    
    def test_next_page_immutable(self):
        """next_page()가 새로운 인스턴스를 반환하는 테스트 (불변성)"""
        original = PaginationState(
            current_page=1,
            items_per_page=10,
            total_items=37
        )
        
        next_pagination = original.next_page()
        
        # 원본은 변경되지 않음
        assert original.current_page == 1
        # 새 인스턴스 생성
        assert next_pagination.current_page == 2
        assert original is not next_pagination
    
    def test_next_page_on_last_page(self):
        """마지막 페이지에서 next_page() 호출 시 변경 없음 테스트"""
        pagination = PaginationState(
            current_page=4,
            items_per_page=10,
            total_items=37
        )
        
        next_pagination = pagination.next_page()
        
        assert next_pagination.current_page == 4
    
    def test_prev_page_immutable(self):
        """prev_page()가 새로운 인스턴스를 반환하는 테스트 (불변성)"""
        original = PaginationState(
            current_page=2,
            items_per_page=10,
            total_items=37
        )
        
        prev_pagination = original.prev_page()
        
        # 원본은 변경되지 않음
        assert original.current_page == 2
        # 새 인스턴스 생성
        assert prev_pagination.current_page == 1
        assert original is not prev_pagination
    
    def test_prev_page_on_first_page(self):
        """첫 페이지에서 prev_page() 호출 시 변경 없음 테스트"""
        pagination = PaginationState(
            current_page=1,
            items_per_page=10,
            total_items=37
        )
        
        prev_pagination = pagination.prev_page()
        
        assert prev_pagination.current_page == 1
    
    def test_change_items_per_page(self):
        """change_items_per_page() 로직 테스트"""
        original = PaginationState(
            current_page=2,
            items_per_page=10,
            total_items=37
        )
        
        # 항목 수를 20으로 변경
        new_pagination = original.change_items_per_page(20)
        
        # 첫 페이지로 리셋 및 items_per_page 변경
        assert new_pagination.current_page == 1
        assert new_pagination.items_per_page == 20
        assert new_pagination.total_items == 37
        assert new_pagination.total_pages == 2  # ceil(37/20)
        # 원본은 변경되지 않음
        assert original.current_page == 2


class TestListViewState:
    """ListViewState 모델 테스트"""
    
    def test_list_view_state_creation(self):
        """정상적인 ListViewState 생성 테스트"""
        items = [
            QAListItem(
                question="Q1",
                answer="A1",
                id="id1",
                created_at="2026-03-05T10:00:00"
            ),
            QAListItem(
                question="Q2",
                answer="A2",
                id="id2",
                created_at="2026-03-05T11:00:00"
            )
        ]
        pagination = PaginationState(
            current_page=1,
            items_per_page=10,
            total_items=2
        )
        
        view = ListViewState(
            items=items,
            pagination=pagination,
            is_empty=False
        )
        
        assert len(view.items) == 2
        assert view.pagination.current_page == 1
        assert view.is_empty is False
        assert view.error_message is None
    
    def test_list_view_state_empty_factory(self):
        """empty() 팩토리 메서드 테스트"""
        view = ListViewState.empty()
        
        assert len(view.items) == 0
        assert view.is_empty is True
        assert view.pagination.total_items == 0
        assert view.error_message is None
    
    def test_list_view_state_error_factory(self):
        """error() 팩토리 메서드 테스트"""
        error_msg = "Failed to fetch items from database"
        view = ListViewState.error(error_msg)
        
        assert len(view.items) == 0
        assert view.is_empty is True
        assert view.error_message == error_msg
        assert view.has_error() is True
    
    def test_list_view_state_has_error(self):
        """has_error() 메서드 테스트"""
        view_no_error = ListViewState.empty()
        assert view_no_error.has_error() is False
        
        view_with_error = ListViewState.error("Some error")
        assert view_with_error.has_error() is True
    
    def test_list_view_state_get_display_message_with_error(self):
        """get_display_message()가 오류 메시지 반환 테스트"""
        error_msg = "Database connection failed"
        view = ListViewState.error(error_msg)
        
        assert view.get_display_message() == error_msg
    
    def test_list_view_state_get_display_message_empty(self):
        """get_display_message()가 빈 목록 메시지 반환 테스트"""
        view = ListViewState.empty()
        
        assert view.get_display_message() == "등록된 질문답변이 없습니다"
    
    def test_list_view_state_get_display_message_has_items(self):
        """get_display_message()가 빈 문자열 반환 테스트 (항목 있을 때)"""
        items = [
            QAListItem(
                question="Q1",
                answer="A1",
                id="id1",
                created_at="2026-03-05T10:00:00"
            )
        ]
        pagination = PaginationState(total_items=1)
        view = ListViewState(items=items, pagination=pagination)
        
        assert view.get_display_message() == ""
