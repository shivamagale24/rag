import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams
)


class VectorStore:

    def __init__(
        self,
        dimension,
        recreate=False
    ):
        self.collection_name = (
            "enterprise_documents"
        )

        self.client = QdrantClient(
            path="data/qdrant"
        )

        if recreate:
            try:
                self.client.delete_collection(
                    self.collection_name
                )
            except Exception:
                pass

        collections = (
            self.client.get_collections()
        )

        collection_names = [
            collection.name
            for collection in collections.collections
        ]

        if (
            self.collection_name
            not in collection_names
        ):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE
                )
            )

    def _build_filter(
        self,
        source=None,
        file_type=None
    ):
        conditions = []

        if source:
            conditions.append(
                FieldCondition(
                    key="source",
                    match=MatchValue(
                        value=source
                    )
                )
            )

        if file_type:
            conditions.append(
                FieldCondition(
                    key="file_type",
                    match=MatchValue(
                        value=file_type
                    )
                )
            )

        if not conditions:
            return None

        return Filter(
            must=conditions
        )

    def add_embeddings(
        self,
        embeddings,
        chunks
    ):
        points = []

        for embedding, chunk in zip(
            embeddings,
            chunks
        ):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload={
                    "text": chunk.get(
                        "text",
                        ""
                    ),
                    "source": chunk.get(
                        "source"
                    ),
                    "document_name": chunk.get(
                        "document_name"
                    ),
                    "file_type": chunk.get(
                        "file_type"
                    ),
                    "chunk_id": chunk.get(
                        "chunk_id"
                    ),
                    "chunk_length": chunk.get(
                        "chunk_length",
                        len(
                            chunk.get(
                                "text",
                                ""
                            )
                        )
                    )
                }
            )

            points.append(point)

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

    def search(
        self,
        query_embedding,
        top_k=3,
        source=None,
        file_type=None
    ):
        query_filter = self._build_filter(
            source=source,
            file_type=file_type
        )

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding.tolist(),
            limit=top_k,
            query_filter=query_filter
        )

        return response.points

    def get_all_chunks(self):
        points = []

        offset = None

        while True:

            batch, offset = (
                self.client.scroll(
                    collection_name=self.collection_name,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
            )

            points.extend(batch)

            if offset is None:
                break

        return points

    def get_chunks_by_ids(
        self,
        ids
    ):
        if not ids:
            return []

        return self.client.retrieve(
            collection_name=self.collection_name,
            ids=ids,
            with_payload=True,
            with_vectors=False
        )

    def delete_document(
        self,
        filename
    ):
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="source",
                        match=MatchValue(
                            value=filename
                        )
                    )
                ]
            )
        )

    def close(self):
        self.client.close()