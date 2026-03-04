"""삭제 다이얼로그 상태 관리 단위 테스트"""

from src.models.qa_list_models import QAListItem
from src.ui.admin_list_tab import _default_deletion_state, _build_delete_choices


def test_default_deletion_state_values():
    state = _default_deletion_state()

    assert state["show_dialog"] is False
    assert state["selected_qa_id"] is None
    assert state["selected_question_preview"] is None
    assert state["is_deleting"] is False


def test_build_delete_choices_with_items():
    items = [
        QAListItem(
            question="삭제 대상 질문입니다",
            answer="답변",
            id="hash_abcdef12",
            created_at="2026-03-05T10:00:00",
        )
    ]

    choices = _build_delete_choices(items)

    assert len(choices) == 1
    label, value = choices[0]
    assert "hash_abc" in label
    assert value == "hash_abcdef12"


def test_build_delete_choices_empty():
    assert _build_delete_choices([]) == []
