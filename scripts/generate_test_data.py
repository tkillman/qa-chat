"""테스트 데이터 생성 스크립트

ChromaDB에 30개의 테스트 Q&A 항목을 생성합니다.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# src 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.chromadb_service import ChromaDBService


def generate_test_data(count: int = 30) -> None:
    """테스트 데이터 생성
    
    Args:
        count: 생성할 항목 수 (기본값: 30)
    """
    service = ChromaDBService()
    
    print(f"🔄 {count}개의 테스트 Q&A 항목 생성 중...")
    
    for i in range(1, count + 1):
        # 시간차를 두어 created_at이 서로 다르도록 설정
        created_at = datetime.now() - timedelta(days=count - i)
        
        question = f"테스트 질문 {i}: Python에서 {i}번째 개념은 무엇인가요?"
        answer = f"테스트 답변 {i}: 이것은 Python 관련 {i}번째 항목에 대한 설명입니다. 상세한 답변 내용이 여기에 들어갑니다."
        
        metadata = {
            "answer": answer,
            "created_at": created_at.isoformat(),
            "source": "test_data",
            "index": i
        }
        
        try:
            service.add_qa(
                question=question,
                answer=answer,
                metadata=metadata
            )
            print(f"✅ [{i}/{count}] {question[:50]}... 추가됨")
        except Exception as e:
            print(f"❌ [{i}/{count}] 오류 발생: {e}")
    
    print(f"\n✨ {count}개의 테스트 데이터 생성 완료!")
    
    # 생성된 항목 확인
    all_items = service.collection.get()
    print(f"\n📊 현재 전체 항목 수: {len(all_items['ids'])}")


if __name__ == "__main__":
    try:
        count = int(sys.argv[1]) if len(sys.argv) > 1 else 30
        generate_test_data(count)
    except ValueError:
        print("❌ 오류: 첫 번째 인자는 숫자여야 합니다 (기본값: 30)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 스크립트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
