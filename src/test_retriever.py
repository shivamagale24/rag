from embeddings import EmbeddingService
from vector_store import VectorStore
from retriever import Retriever


def main():

    print("Starting Retriever test...")

    embedding_service = EmbeddingService()

    vector_store = VectorStore(
        dimension=384
    )

    retriever = Retriever(
        embedding_service,
        vector_store
    )

    question = "What is ISO/IEC 27001?"

    print()
    print("Calling Retriever...")
    print()

    results = retriever.retrieve(
        question,
        top_k=5
    )

    print()
    print(
        "Retriever results:",
        len(results)
    )

    print()

    for index, result in enumerate(
        results,
        start=1
    ):

        print(
            f"{index}. "
            f"{result['source']} | "
            f"Chunk {result['chunk_id']}"
        )

        print(
            f"Score: "
            f"{result['score']:.4f}"
        )

        print(
            "Text:",
            result["text"][:300]
        )

        print(
            "-" * 60
        )

    vector_store.close()


if __name__ == "__main__":
    main()