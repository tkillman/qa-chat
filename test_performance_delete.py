"""성능 검증 스크립트 - 삭제 성능 측정"""
import time
import sys
from pathlib import Path

# 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.services.qa_delete_service import get_qa_delete_service
from src.models.qa_delete_models import QADeleteRequest
from src.services.qa_update_service import QAUpdateService
from src.services.chromadb_service import get_chromadb_service

def measure_delete_performance():
    """삭제 성능 측정"""
    print("🔍 성능 검증 시작...")
    
    # ChromaDB 초기화
    chromadb = get_chromadb_service()
    
    # 테스트 항목 생성
    print("  1. 테스트 항목 생성 중...")
    update_service = QAUpdateService()
    test_questions = []
    
    for i in range(10):
        question = f'Performance test question {i}'
        answer = f'Performance test answer {i}'
        update_service.update_qa(question, answer)
        test_questions.append(question)
    
    print(f"     ✓ {len(test_questions)}개 항목 생성 완료")
    
    # 삭제 성능 측정
    print("  2. 삭제 성능 측정 중...")
    delete_service = get_qa_delete_service()
    
    # 5개 항목 삭제
    start_time = time.time()
    deleted_count = 0
    
    for i, question in enumerate(test_questions[:5]):
        # QAItem의 hash_key 방식으로 ID 생성
        from src.models.qa_item import QAItem
        qa_item = QAItem(question=question, answer="dummy")
        qa_id = qa_item.get_hash_key()
        
        request = QADeleteRequest(qa_id=qa_id, admin_user='perf_test')
        result = delete_service.delete_qa_item(request)
        
        if result.success:
            deleted_count += 1
    
    elapsed = time.time() - start_time
    avg_time = elapsed / deleted_count if deleted_count > 0 else 0
    
    # 결과 출력
    print(f"\n✅ 성능 검증 결과:")
    print(f"  - {deleted_count}개 항목 삭제 총 시간: {elapsed:.3f}초")
    print(f"  - 항목당 평균 시간: {avg_time:.3f}초")
    print(f"  - 목표 < 2초: {'✅ PASS' if avg_time < 2.0 else '❌ FAIL'}")
    
    # 메모리 체크
    import psutil
    import os
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"  - 현재 메모리 사용량: {memory_mb:.2f} MB")
    
    return avg_time < 2.0

if __name__ == "__main__":
    try:
        passed = measure_delete_performance()
        sys.exit(0 if passed else 1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
