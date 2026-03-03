"""
QA 항목 데이터 모델
"""
from dataclasses import dataclass, asdict
import json
from typing import Optional, List


@dataclass
class QAItem:
    """질문-답변 항목 데이터 클래스
    
    Attributes:
        question (str): 사용자 질문
        answer (str): 답변 텍스트
        embedding (Optional[List[float]]): 질문의 임베딩 벡터
        metadata (dict): 메타데이터 (작성자, 생성시간 등)
    """
    question: str
    answer: str
    embedding: Optional[List[float]] = None
    metadata: Optional[dict] = None
    
    def __post_init__(self):
        """초기화 후 메타데이터 기본값 설정"""
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> dict:
        """데이터 클래스를 딕셔너리로 변환"""
        return {
            "question": self.question,
            "answer": self.answer,
            "metadata": self.metadata
        }
    
    def to_json_line(self) -> str:
        """JSON 한 줄로 변환 (init.txt 저장 형식)"""
        line_dict = self.to_dict()
        return json.dumps(line_dict, ensure_ascii=False)
    
    @classmethod
    def from_json_line(cls, line: str) -> "QAItem":
        """JSON 한 줄에서 QAItem 생성"""
        try:
            data = json.loads(line)
            return cls(
                question=data.get("question", ""),
                answer=data.get("answer", ""),
                metadata=data.get("metadata", {})
            )
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid JSON line format: {line}") from e
    
    def get_hash_key(self) -> str:
        """질문 기반 고유 키 생성 (중복 검사용)"""
        return self.question.strip().lower()
