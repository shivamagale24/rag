import os
import sys


# Allow imports from src/
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "src"
        )
    )
)


from embeddings import EmbeddingService
from vector_store import VectorStore
from retriever import Retriever


# =========================================================
# TEST QUESTIONS
# =========================================================

TEST_CASES = [

    {
        "question":
            "What programming languages are mentioned in the resume?",

        "expected_source":
            "resume.pdf"
    },

    {
        "question":
            "What is ISO 27001?",

        "expected_source":
            "iso27001.pdf"
    }

]


# =========================================================
# MAIN
# =========================================================

def main():

    embedding_service = (
        EmbeddingService()
    )


    vector_store = VectorStore(
        dimension=384
    )


    retriever = Retriever(

        embedding_service,

        vector_store

    )


    total = len(
        TEST_CASES
    )

    hits_at_5 = 0


    print()
    print(
        "RAG Retrieval Evaluation"
    )
    print("=" * 60)


    for case in TEST_CASES:

        question = case[
            "question"
        ]

        expected = case[
            "expected_source"
        ]


        results = retriever.retrieve(

            question,

            top_k=5

        )


        sources = [

            result["source"]

            for result in results

        ]


        found = (
            expected
            in sources
        )


        if found:

            hits_at_5 += 1


        print()
        print(
            f"Question: {question}"
        )

        print(
            f"Expected: {expected}"
        )

        print(
            f"Retrieved: {sources}"
        )

        print(
            f"Hit@5: {found}"
        )


    score = (

        hits_at_5 / total

        if total > 0

        else 0

    )


    print()
    print("=" * 60)

    print(
        f"Recall@5: {score:.2%}"
    )

    print()


    vector_store.close()


if __name__ == "__main__":

    main()