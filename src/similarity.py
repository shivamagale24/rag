import numpy as np


def cosine_similarity(
    vector1,
    vector2
):
    vector1 = np.asarray(vector1)
    vector2 = np.asarray(vector2)

    denominator = (
        np.linalg.norm(vector1)
        * np.linalg.norm(vector2)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(vector1, vector2)
        / denominator
    )


def retrieve(
    question_embedding,
    chunks,
    chunk_embeddings,
    top_k=3
):
    results = []

    for chunk, embedding in zip(
        chunks,
        chunk_embeddings
    ):
        score = cosine_similarity(
            question_embedding,
            embedding
        )

        results.append(
            {
                "chunk": chunk,
                "score": score
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]