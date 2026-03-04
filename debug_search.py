import chromadb
from src.services.embedding_service import EmbeddingService

# ChromaDB 직접 접근
client = chromadb.PersistentClient(path='.chroma')
collection = client.get_collection(name='qa_items')

# 컬렉션 데이터 확인
data = collection.get()
print(f"Collection data:")
print(f"  IDs: {data['ids']}")
print(f"  Documents: {data['documents']}")
print(f"  Has embeddings: {data['embeddings'] is not None}")

# 임베딩 생성
embedding_service = EmbeddingService()
query = '너는 누구니'
query_embedding = embedding_service.embed_text(query)
print(f"\nQuery embedding shape: {len(query_embedding)}")

# ChromaDB 직접 쿼리
print(f"\nDirect ChromaDB query:")
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=1,
    include=["documents", "metadatas", "distances"]
)
print(f"IDs: {results['ids']}")
print(f"Distances: {results['distances']}")
print(f"Documents: {results['documents']}")
if results['distances'][0]:
    distance = results['distances'][0][0]
    similarity = 1 - distance
    print(f"Distance: {distance:.4f}")
    print(f"Similarity: {similarity:.4f}")
