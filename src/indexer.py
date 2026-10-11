import os

from chunker import chunk_text
from embeddings import EmbeddingService
from loader import load_document


DOCUMENT_FOLDER = "data/documents"


def index_document(
    file_path,
    vector_store
):
    print(
        f"Indexing document: {file_path}"
    )

    # =====================================================
    # Load Document
    # =====================================================

    text = load_document(
        file_path
    )

    if not text.strip():
        raise ValueError(
            "Document contains no readable text."
        )


    # =====================================================
    # Create Chunks
    # =====================================================

    chunks = chunk_text(
        text,
        chunk_size=500,
        overlap=100
    )

    if not chunks:
        raise ValueError(
            "No chunks were created from the document."
        )


    # =====================================================
    # Document Metadata
    # =====================================================

    filename = os.path.basename(
        file_path
    )

    file_type = (
        os.path.splitext(filename)[1]
        .lower()
        .replace(".", "")
    )


    # =====================================================
    # Prepare Document Chunks
    # =====================================================

    document_chunks = []

    for index, chunk in enumerate(chunks):

        document_chunks.append(
            {
                "text": chunk,
                "source": filename,
                "document_name": filename,
                "file_type": file_type,
                "chunk_id": index,
                "chunk_length": len(chunk)
            }
        )


    # =====================================================
    # Generate Embeddings
    # =====================================================

    embedding_service = EmbeddingService()

    texts = [
        chunk["text"]
        for chunk in document_chunks
    ]

    embeddings = (
        embedding_service.generate_embeddings(
            texts
        )
    )


    # =====================================================
    # Store Embeddings
    # =====================================================

    vector_store.add_embeddings(
        embeddings,
        document_chunks
    )


    print(
        f"Indexed {len(document_chunks)} chunks "
        f"from {filename}"
    )

    return {
        "filename": filename,
        "chunks": len(document_chunks)
    }


def main():

    if not os.path.exists(
        DOCUMENT_FOLDER
    ):
        print(
            "Document folder does not exist."
        )
        return


    # =====================================================
    # Initialize Vector Store
    # =====================================================

    from vector_store import VectorStore

    vector_store = VectorStore(
        dimension=384,
        recreate=True
    )


    try:

        files = sorted(
            os.listdir(
                DOCUMENT_FOLDER
            )
        )

        for filename in files:

            file_path = os.path.join(
                DOCUMENT_FOLDER,
                filename
            )

            if not os.path.isfile(
                file_path
            ):
                continue

            extension = (
                os.path.splitext(filename)[1]
                .lower()
            )

            if extension not in {
                ".pdf",
                ".txt",
                ".docx"
            }:
                continue

            try:
                index_document(
                    file_path,
                    vector_store
                )

            except Exception as exc:
                print(
                    f"Failed to index "
                    f"{filename}: {exc}"
                )

    finally:

        vector_store.close()


if __name__ == "__main__":
    main()