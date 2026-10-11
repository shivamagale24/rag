from embeddings import EmbeddingService
from vector_store import VectorStore


def main():

    print("Starting direct Qdrant test...")

    embedding_service = EmbeddingService()

    vector_store = VectorStore(
        dimension=384
    )

    question = "What is ISO/IEC 27001?"

    print()
    print("Generating query embedding...")

    query_embedding = (
        embedding_service
        .generate_embedding(question)
    )

    print(
        "Embedding dimension:",
        len(query_embedding)
    )

    print()
    print("Searching Qdrant...")

    results = (
        vector_store.search(
            query_embedding,
            top_k=10
        )
    )

    print()
    print(
        "Results:",
        len(results)
    )

    print()

    for index, point in enumerate(
        results,
        start=1
    ):

        payload = point.payload

        print(
            f"{index}. "
            f"Score: {point.score:.4f} | "
            f"Source: {payload.get('source')} | "
            f"Chunk: {payload.get('chunk_id')}"
        )

        print(
            "Text:",
            payload.get("text", "")[:300]
        )

        print(
            "-" * 60
        )

    vector_store.close()


if __name__ == "__main__":
    main()