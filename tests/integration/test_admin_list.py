"""테스트: 관리자 목록 조회 통합 테스트

이 모듈은 관리자 로그인 후 목록 조회 탭의 전체 동작을 검증합니다.
"""

import pytest
import sys
from pathlib import Path

# src 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from models.qa_list_models import QAListItem, ListViewState


class TestAdminListIntegration:
    """관리자 목록 조회 통합 테스트"""
    
    def test_admin_list_view_state_requires_items(self):
        """목록 조회 UI가 ListViewState를 필요로 함 확인"""
        # UI에서 필요한 상태
        view_state = ListViewState.empty()
        
        assert hasattr(view_state, 'items')
        assert hasattr(view_state, 'pagination')
        assert hasattr(view_state, 'is_empty')
        assert hasattr(view_state, 'error_message')
    
    def test_admin_list_empty_state_handling(self):
        """빈 목록 상태 처리 테스트"""
        view_state = ListViewState.empty()
        
        # UI는 빈 상태에서 페이징 컨트롤 숨김
        assert view_state.is_empty is True
        assert len(view_state.items) == 0
        assert view_state.get_display_message() == "등록된 질문답변이 없습니다"
    
    def test_admin_list_error_state_handling(self):
        """오류 상태 처리 테스트"""
        error_msg = "데이터베이스 연결 실패"
        view_state = ListViewState.error(error_msg)
        
        # UI는 오류 메시지 표시
        assert view_state.has_error() is True
        assert view_state.get_display_message() == error_msg
        assert view_state.is_empty is True
    
    def test_admin_list_items_display_format(self):
        """목록 항목 표시 형식 확인 테스트"""
        item = QAListItem(
            question="Python 튜플이란?",
            answer="Python 튜플은 불변 시퀀스입니다.",
            id="test_id",
            created_at="2026-03-05T10:00:00"
        )
        
        # 항목이 구독자에게 필요한 모든 필드를 가짐
        assert item.question is not None
        assert item.answer is not None
        assert item.id is not None
        assert item.created_at is not None
    
    def test_admin_list_pagination_control_visibility(self):
        """페이징 컨트롤 표시 여부 테스트"""
        # 항목이 있을 때
        items = [
            QAListItem(
                question="Q1",
                answer="A1",
                id="id1",
                created_at="2026-03-05T10:00:00"
            )
        ]
        from models.qa_list_models import PaginationState
        pagination = PaginationState(
            current_page=1,
            items_per_page=10,
            total_items=1
        )
        
        view = ListViewState(items=items, pagination=pagination)
        
        # 페이징 컨트롤 표시됨
        assert view.is_empty is False
        assert view.pagination.get_page_info_text() is not None
    
    def test_admin_list_multiple_items_sorted_by_date(self):
        """여러 항목이 날짜순 정렬된 상태 확인 테스트"""
        # 최신순(내림차순)으로 정렬되어야 함
        items = [
            QAListItem(
                question="Q3",
                answer="A3",
                id="id3",
                created_at="2026-03-05T14:00:00"  # 가장 최신
            ),
            QAListItem(
                question="Q2",
                answer="A2",
                id="id2",
                created_at="2026-03-05T12:00:00"  # 중간
            ),
            QAListItem(
                question="Q1",
                answer="A1",
                id="id1",
                created_at="2026-03-05T10:00:00"  # 가장 오래됨
            ),
        ]
        
        # 최신순 정렬 검증
        created_times = [item.created_at for item in items]
        
        # 내림차순 확인
        assert created_times[0] > created_times[1]
        assert created_times[1] > created_times[2]
    
    def test_admin_list_page_navigation(self):
        """페이지 네비게이션 기능 테스트"""
        from models.qa_list_models import PaginationState
        
        # 총 37개 항목, 페이지당 10개
        pagination = PaginationState(
            current_page=1,
            items_per_page=10,
            total_items=37
        )
        
        # 첫 페이지: 이전 불가, 다음 가능
        assert pagination.has_prev() is False
        assert pagination.has_next() is True
        
        # 다음 페이지로
        next_pagination = pagination.next_page()
        assert next_pagination.current_page == 2
        assert next_pagination.has_prev() is True
        assert next_pagination.has_next() is True
        
        # 마지막 페이지(4페이지)로
        last_pagination = PaginationState(
            current_page=4,
            items_per_page=10,
            total_items=37
        )
        assert last_pagination.has_prev() is True
        assert last_pagination.has_next() is False
    
    def test_admin_list_page_info_display(self):
        """페이지 정보 표시 형식 테스트"""
        from models.qa_list_models import PaginationState
        
        pagination = PaginationState(
            current_page=2,
            items_per_page=10,
            total_items=37
        )
        
        # UI에 표시될 페이지 정보
        page_info = pagination.get_page_info_text()
        assert page_info == "페이지 2/4"
    
    def test_admin_list_total_items_display(self):
        """전체 항목 수 표시 형식 테스트"""
        from models.qa_list_models import PaginationState
        
        pagination = PaginationState(
            current_page=1,
            items_per_page=10,
            total_items=37
        )
        
        # UI에 표시될 전체 항목 수
        total_text = pagination.get_total_items_text()
        assert total_text == "총 37개의 항목"
    
    def test_admin_list_items_per_page_selection(self):
        """페이지당 항목 수 선택 기능 테스트"""
        from models.qa_list_models import PaginationState
        
        original = PaginationState(
            current_page=2,
            items_per_page=10,
            total_items=100
        )
        
        # 20개/페이지로 변경
        new_pagination = original.change_items_per_page(20)
        
        # 첫 페이지로 리셋, 항목 수 변경
        assert new_pagination.current_page == 1
        assert new_pagination.items_per_page == 20
        assert new_pagination.total_pages == 5  # ceil(100/20)
        
        # 원본은 변경 없음 (불변성)
        assert original.current_page == 2
        assert original.items_per_page == 10


class TestAdminListEdgeCases:
    """담당자 목록 조회 엣지 케이스 테스트"""
    
    def test_admin_list_single_item(self):
        """단일 항목만 있을 때 테스트"""
        items = [
            QAListItem(
                question="유일한 질문",
                answer="유일한 답변",
                id="only_one",
                created_at="2026-03-05T10:00:00"
            )
        ]
        from models.qa_list_models import PaginationState
        pagination = PaginationState(total_items=1)
        
        view = ListViewState(items=items, pagination=pagination)
        
        assert len(view.items) == 1
        assert view.is_empty is False
        assert view.pagination.total_pages == 1
    
    def test_admin_list_exactly_page_boundary(self):
        """정확하게 페이지 경계에 맞을 때 테스트"""
        # 정확히 20개 항목 (2페이지, 각 10개)
        from models.qa_list_models import PaginationState
        pagination = PaginationState(
            current_page=1,
            items_per_page=10,
            total_items=20
        )
        
        assert pagination.total_pages == 2
        assert pagination.has_next() is True
        
        # 마지막 페이지
        last = PaginationState(
            current_page=2,
            items_per_page=10,
            total_items=20
        )
        assert last.has_next() is False
    
    def test_admin_list_one_item_over_boundary(self):
        """페이지 경계를 1개 초과할 때 테스트"""
        # 21개 항목 (2페이지, 10+10+1)
        from models.qa_list_models import PaginationState
        pagination = PaginationState(
            current_page=1,
            items_per_page=10,
            total_items=21
        )
        
        assert pagination.total_pages == 3
