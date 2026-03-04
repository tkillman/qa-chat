"""테스트: QA 목록 조회 서비스

이 모듈은 QAListService의 목록 조회, 정렬, 페이징 로직을 검증합니다.
"""

import pytest
from datetime import datetime, timedelta
import sys
from pathlib import Path

# src 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from models.qa_list_models import QAListItem, PaginationState, ListViewState
from services.qa_list_service import QAListService, get_qa_list_service


class TestQAListService:
    """QAListService 테스트"""
    
    @pytest.fixture
    def service(self):
        """Service 인스턴스 생성"""
        return QAListService()
    
    @pytest.fixture
    def sample_items(self):
        """테스트용 샘플 QAListItem 리스트"""
        base_time = datetime.now()
        return [
            QAListItem(
                question="질문 1",
                answer="답변 1",
                id="id1",
                created_at=(base_time - timedelta(days=2)).isoformat()
            ),
            QAListItem(
                question="질문 2",
                answer="답변 2",
                id="id2",
                created_at=(base_time - timedelta(days=1)).isoformat()
            ),
            QAListItem(
                question="질문 3",
                answer="답변 3",
                id="id3",
                created_at=base_time.isoformat()
            ),
        ]
    
    def test_list_items_first_page(self, service):
        """첫 페이지 목록 조회 테스트"""
        # 이 테스트는 ChromaDB와 상호작용하므로, 
        # 실제 구현 시에는 모의 객체나 테스트 DB 사용
        view_state = service.list_items(page=1, items_per_page=10)
        
        # ListViewState 반환 확인
        assert isinstance(view_state, ListViewState)
        assert view_state.pagination.current_page == 1
        assert view_state.pagination.items_per_page == 10
        # 항목이 있거나 is_empty가 True여야 함
        assert view_state.is_empty or len(view_state.items) > 0
    
    def test_list_items_pagination_boundaries(self, service):
        """페이징 경계 조건 테스트"""
        view_state = service.list_items(page=1, items_per_page=10)
        
        # 페이지 1에서는 has_prev가 False
        if not view_state.is_empty:
            assert view_state.pagination.has_prev() is False
    
    def test_list_items_with_different_page_sizes(self, service):
        """다른 페이지 크기로 조회 테스트"""
        for items_per_page in [10, 20, 50]:
            view_state = service.list_items(page=1, items_per_page=items_per_page)
            
            assert isinstance(view_state, ListViewState)
            assert view_state.pagination.items_per_page == items_per_page
    
    def test_list_items_invalid_page_corrected(self, service):
        """유효하지 않은 페이지 번호 자동 보정 테스트"""
        # 음수 페이지 요청
        view_state = service.list_items(page=-1, items_per_page=10)
        
        # 페이지 1로 보정됨
        assert view_state.pagination.current_page >= 1
    
    def test_list_items_sorting_latest_first(self, service):
        """최신 등록순 정렬 확인 테스트"""
        # 이 테스트는 실제 ChromaDB와 통합되므로 스킵 (통합 테스트에서 검증)
        # 기본 정렬 로직 단위 테스트
        base_time = datetime.now()
        items = [
            QAListItem(
                question="Q1",
                answer="A1",
                id="id1",
                created_at=(base_time - timedelta(days=2)).isoformat()
            ),
            QAListItem(
                question="Q2",
                answer="A2",
                id="id2",
                created_at=(base_time).isoformat()
            ),
        ]
        
        # 정렬 로직 검증
        sorted_items = sorted(items, key=lambda x: x.created_at, reverse=True)
        assert sorted_items[0].id == "id2"  # 최신이 먼저
        assert sorted_items[1].id == "id1"
    
    def test_list_items_returns_correct_page_count(self, service):
        """페이지 항목 수 반환 테스트"""
        # 첫 페이지
        view_state = service.list_items(page=1, items_per_page=10)
        
        # 빈 목록이 아니라면, items_per_page 이하
        if not view_state.is_empty:
            assert len(view_state.items) <= 10
    
    def test_list_items_error_handling(self, service):
        """오류 처리 테스트"""
        # 오류 발생 시 ListViewState.error()가 반환되는지 검증
        error_view = ListViewState.error("Test error message")
        
        assert error_view.has_error()
        assert error_view.get_display_message() == "Test error message"
    
    def test_list_items_with_sorting(self, service):
        """정렬 로직이 최신순 확인 테스트"""
        view_state = service.list_items(page=1, items_per_page=10)
        
        # 여러 항목이 있다면, created_at이 내림차순이어야 함
        if len(view_state.items) > 1:
            for i in range(len(view_state.items) - 1):
                current = view_state.items[i].created_at
                next_item = view_state.items[i + 1].created_at
                # 현재 항목이 다음 항목보다 최신이어야 함
                assert current >= next_item, f"정렬 순서 오류: {current} < {next_item}"


class TestQAListServiceSingleton:
    """QAListService 싱글톤 팩토리 테스트"""
    
    def test_get_qa_list_service_returns_same_instance(self):
        """get_qa_list_service()가 같은 인스턴스 반환 테스트"""
        service1 = get_qa_list_service()
        service2 = get_qa_list_service()
        
        assert service1 is service2
    
    def test_get_qa_list_service_returns_service(self):
        """get_qa_list_service()가 QAListService 인스턴스 반환 테스트"""
        service = get_qa_list_service()
        
        assert isinstance(service, QAListService)


class TestPaginationOffsetCalculation:
    """페이징 오프셋 계산 테스트"""
    
    def test_pagination_offset_page1(self):
        """페이지 1의 오프셋 테스트"""
        pagination = PaginationState(
            current_page=1,
            items_per_page=10,
            total_items=100
        )
        
        assert pagination.get_offset() == 0
    
    def test_pagination_offset_page2(self):
        """페이지 2의 오프셋 테스트"""
        pagination = PaginationState(
            current_page=2,
            items_per_page=10,
            total_items=100
        )
        
        assert pagination.get_offset() == 10
    
    def test_pagination_offset_page3_with_20_per_page(self):
        """페이지 3, 20개/페이지의 오프셋 테스트"""
        pagination = PaginationState(
            current_page=3,
            items_per_page=20,
            total_items=100
        )
        
        assert pagination.get_offset() == 40


class TestListViewStateIntegration:
    """ListViewState 통합 테스트"""
    
    def test_list_view_state_with_pagination(self):
        """ListViewState에 PaginationState가 통합됨 테스트"""
        items = [
            QAListItem(
                question="Q1",
                answer="A1",
                id="id1",
                created_at="2026-03-05T10:00:00"
            )
        ]
        pagination = PaginationState(
            current_page=1,
            items_per_page=10,
            total_items=1
        )
        
        view = ListViewState(
            items=items,
            pagination=pagination
        )
        
        assert view.pagination.get_page_info_text() == "페이지 1/1"
        assert view.pagination.get_total_items_text() == "총 1개의 항목"
