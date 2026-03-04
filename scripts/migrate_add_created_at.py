"""마이그레이션 스크립트: 기존 데이터에 created_at 메타데이터 추가

기존 Q&A 항목의 메타데이터에 created_at 필드를 추가합니다.
이미 created_at이 있는 항목은 건너뜁니다.
"""

import sys
from pathlib import Path
from datetime import datetime

# src 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.chromadb_service import ChromaDBService


def migrate_add_created_at() -> None:
    """기존 데이터에 created_at 추가
    
    현재 시간을 기본값으로 사용합니다.
    """
    service = ChromaDBService()
    collection = service.collection
    
    print("🔄 기존 Q&A 항목에 created_at 메타데이터 추가 중...")
    
    # 모든 항목 조회
    all_items = collection.get()
    
    if not all_items["ids"]:
        print("ℹ️  마이그레이션할 항목이 없습니다.")
        return
    
    total_count = len(all_items["ids"])
    updated_count = 0
    
    print(f"📊 전체 항목 수: {total_count}")
    
    for i, (id, metadata) in enumerate(zip(all_items["ids"], all_items["metadatas"])):
        # created_at이 이미 있으면 건너뛰기
        if "created_at" in metadata:
            print(f"⏭️  [{i+1}/{total_count}] {id[:8]}... 이미 created_at 있음")
            continue
        
        # 새로운 created_at 설정
        metadata["created_at"] = datetime.now().isoformat()
        
        try:
            # 메타데이터 업데이트
            collection.update(
                ids=[id],
                metadatas=[metadata]
            )
            updated_count += 1
            print(f"✅ [{i+1}/{total_count}] {id[:8]}... 업데이트됨")
        except Exception as e:
            print(f"❌ [{i+1}/{total_count}] {id[:8]}... 오류: {e}")
    
    print(f"\n✨ 마이그레이션 완료! {updated_count}/{total_count}개 항목 업데이트됨")


if __name__ == "__main__":
    try:
        migrate_add_created_at()
    except Exception as e:
        print(f"❌ 마이그레이션 중 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
