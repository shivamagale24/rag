import os


class Retriever:

    def __init__(
        self,
        embedding_service,
        vector_store
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

        self.similarity_threshold = 0.0
        self.candidate_k = 20

    def _get_known_sources(self):
        doc_folder = "data/documents"
        if os.path.exists(doc_folder):
            files = [
                f for f in os.listdir(doc_folder)
                if os.path.isfile(os.path.join(doc_folder, f))
            ]
            if files:
                return sorted(files)

        points = self.vector_store.get_all_chunks()
        sources = {
            pt.payload.get("source")
            for pt in points
            if pt.payload and pt.payload.get("source")
        }
        return sorted(list(sources))

    def _resolve_source(self, question, known_sources):
        q_lower = question.lower()
        for doc in known_sources:
            doc_lower = doc.lower()
            base_name = os.path.splitext(doc_lower)[0]
            if doc_lower in q_lower or base_name in q_lower:
                return doc
            if base_name == "resume" and any(
                term in q_lower for term in ("candidate", "applicant", "cv")
            ):
                return doc
            if "iso" in base_name and "iso" in q_lower:
                return doc
        return None

    def retrieve(
        self,
        question,
        top_k=5,
        source=None,
        file_type=None
    ):
        query_embedding = (
            self.embedding_service.generate_embedding(
                question
            )
        )

        known_sources = self._get_known_sources()

        resolved_source = source
        if not resolved_source:
            resolved_source = self._resolve_source(
                question,
                known_sources
            )

        if resolved_source:
            points = self.vector_store.search(
                query_embedding,
                top_k=self.candidate_k,
                source=resolved_source,
                file_type=file_type
            )
        else:
            points = []
            if known_sources:
                per_doc_k = max(2, self.candidate_k // len(known_sources))
                for doc in known_sources:
                    doc_points = self.vector_store.search(
                        query_embedding,
                        top_k=per_doc_k,
                        source=doc,
                        file_type=file_type
                    )
                    points.extend(doc_points)
            else:
                points = self.vector_store.search(
                    query_embedding,
                    top_k=self.candidate_k,
                    source=None,
                    file_type=file_type
                )

        results = []
        seen = set()

        for point in points:

            payload = point.payload or {}

            text = payload.get(
                "text",
                ""
            )

            if not text:
                continue

            chunk_key = (
                payload.get("source"),
                payload.get("chunk_id")
            )
            if chunk_key in seen:
                continue
            seen.add(chunk_key)

            score = float(
                point.score
            )

            if score < self.similarity_threshold:
                continue

            results.append(
                {
                    "score": score,
                    "keyword_score": 0.0,
                    "hybrid_score": score,
                    "reranker_score": score,
                    "text": text,
                    "source": payload.get(
                        "source"
                    ),
                    "document_name": payload.get(
                        "document_name"
                    ),
                    "file_type": payload.get(
                        "file_type"
                    ),
                    "chunk_id": payload.get(
                        "chunk_id"
                    )
                }
            )

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:top_k]