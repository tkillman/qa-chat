"""통합 테스트: 사용자 질문 검색 흐름 (US4)."""
from unittest.mock import Mock
from src.main import QAChatApp


class TestUserSearchFlow:
    """사용자 탭 검색 end-to-end(앱 레벨) 테스트."""

    def test_user_search_returns_top_result(self):
        app = QAChatApp()
        app.user_search_service = Mock()
        app.user_search_service.search_qa.return_value = [
            {"answer": "프로그래밍 언어입니다", "similarity": 0.91}
        ]

        answer, similarity = app.search_answer("Python이 뭐야?")

        assert answer == "프로그래밍 언어입니다"
        assert similarity == 0.91

    def test_user_search_no_result_uses_exact_message(self):
        app = QAChatApp()
        app.user_search_service = Mock()
        app.user_search_service.search_qa.return_value = []

        answer, similarity = app.search_answer("존재하지 않는 질문")

        assert answer == "답변을 찾을 수 없습니다"
        assert similarity == 0.0

    def test_user_search_question_length_limit(self):
        app = QAChatApp()
        app.user_search_service = Mock()

        answer, similarity = app.search_answer("Q" * 501)

        assert "500자" in answer
        assert similarity == 0.0
