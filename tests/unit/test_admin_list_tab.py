"""관리자 목록 탭 UI 렌더링 테스트"""

from src.models.qa_list_models import ListViewState, PaginationState
from src.models.qa_list_models import QAListItem
from src.ui.admin_list_tab import render_qa_cards, load_list_from_source


def test_render_qa_cards_includes_delete_button():
    items = [
        QAListItem(
            question="테스트 질문",
            answer="테스트 답변",
            id="hash_12345678",
            created_at="2026-03-05T10:00:00"
        )
    ]

    html, visible = render_qa_cards(items, visible=True)

    assert visible is True
    assert "🗑️ 삭제" in html
    assert "title=\"삭제\"" in html


def test_render_qa_cards_empty_hides_list():
    html, visible = render_qa_cards([], visible=True)

    assert visible is False
    assert "등록된 질문답변이 없습니다" in html


class StubListService:
    def __init__(self, responses):
        self._responses = responses
        self.call_count = 0

    def list_items(self, page: int, items_per_page: int):
        response = self._responses[min(self.call_count, len(self._responses) - 1)]
        self.call_count += 1
        return response


def test_load_list_from_source_error_state_no_fallback_items():
    service = StubListService([ListViewState.error("데이터베이스 연결 실패")])

    html, page_info, total_text, current_page = load_list_from_source(service, 1, 10)

    assert service.call_count == 1
    assert "데이터베이스 연결 실패" in html
    assert page_info == "페이지 1/1"
    assert total_text == "오류 발생"
    assert current_page == 1


def test_load_list_from_source_requeries_every_call():
    item = QAListItem(
        question="정본 질문",
        answer="정본 답변",
        id="id-1",
        created_at="2026-03-06T10:00:00"
    )
    view = ListViewState(
        items=[item],
        pagination=PaginationState(current_page=1, items_per_page=10, total_items=1)
    )
    service = StubListService([view, view])

    first = load_list_from_source(service, 1, 10)
    second = load_list_from_source(service, 1, 10)

    assert service.call_count == 2
    assert first[1] == "페이지 1/1"
    assert first[2] == "총 1개의 항목"
    assert second[1] == "페이지 1/1"
    assert second[2] == "총 1개의 항목"
