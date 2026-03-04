"""Pytest 공통 테스트 설정."""
import os
import pytest


@pytest.fixture(autouse=True)
def set_default_env(monkeypatch: pytest.MonkeyPatch):
    """테스트 기본 환경값을 고정한다."""
    monkeypatch.setenv("ADMIN_PASSWORD", os.getenv("ADMIN_PASSWORD", "1234"))
    monkeypatch.setenv("SIMILARITY_THRESHOLD", os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    monkeypatch.setenv("MAX_USER_QUESTION_LENGTH", os.getenv("MAX_USER_QUESTION_LENGTH", "500"))
    monkeypatch.setenv("MAX_ADMIN_QUESTION_LENGTH", os.getenv("MAX_ADMIN_QUESTION_LENGTH", "500"))
    monkeypatch.setenv("MAX_ADMIN_ANSWER_LENGTH", os.getenv("MAX_ADMIN_ANSWER_LENGTH", "2000"))
