"""관리자 목록 탭 UI 렌더링 테스트"""

from src.models.qa_list_models import QAListItem
from src.ui.admin_list_tab import render_qa_cards


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
