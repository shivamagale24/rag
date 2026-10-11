from src.embeddings import EmbeddingService
from src.vector_store import VectorStore
from src.retriever import Retriever


embedding_service = EmbeddingService()
vector_store = VectorStore(dimension=384)
retriever = Retriever(embedding_service, vector_store)


question = "What GenAI skills are mentioned in the resume?"

results = retriever.retrieve(
    question,
    top_k=8
)


print("\n================ RETRIEVAL RESULTS ================\n")

if not results:
    print("NO RESULTS FOUND")
else:
    for i, result in enumerate(results, start=1):
        print(f"RANK: {i}")
        print(f"SOURCE: {result.get('source')}")
        print(f"CHUNK: {result.get('chunk_id')}")
        print(f"VECTOR SCORE: {result.get('score')}")
        print(f"KEYWORD SCORE: {result.get('keyword_score')}")
        print(f"HYBRID SCORE: {result.get('hybrid_score')}")
        print(f"RERANKER SCORE: {result.get('reranker_score')}")
        print("\nTEXT:")
        print(result.get("text"))
        print("\n" + "-" * 60)