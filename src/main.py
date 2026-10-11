from conversation import ConversationMemory


# =========================================================
# ASK QUESTION
# =========================================================

def ask_question(
    question,
    conversation_memory,
    query_rewriter,
    retriever,
    prompt_builder,
    llm_service,
    source_filter=None,
    file_type_filter=None
):

    # =====================================================
    # Get Conversation History
    # =====================================================

    conversation_history = (
        conversation_memory.get_history()
    )


    # =====================================================
    # Rewrite Question
    # =====================================================

    search_question = query_rewriter.rewrite(
        question,
        conversation_history
    )

    if not search_question:
        search_question = question

    search_question = search_question.strip()


    # =====================================================
    # Retrieve Relevant Documents
    # =====================================================

    results = retriever.retrieve(
        search_question,
        top_k=8,
        source=source_filter,
        file_type=file_type_filter
    )


    # =====================================================
    # No Relevant Documents
    # =====================================================

    if not results:

        answer = (
            "I don't know based on the provided documents."
        )

        conversation_memory.add_message(
            question,
            answer
        )

        return {
            "answer": answer,
            "sources": [],
            "search_question": search_question
        }


    # =====================================================
    # Build Context
    # =====================================================

    context_parts = []

    for index, result in enumerate(results, start=1):

        context_parts.append(
            f"[Source {index}]\n"
            f"Document: {result.get('document_name', '')}\n"
            f"Chunk: {result.get('chunk_id', '')}\n"
            f"Content:\n"
            f"{result.get('text', '')}"
        )

    context = "\n\n".join(context_parts)


    # =====================================================
    # Build Prompt
    # =====================================================

    prompt = prompt_builder.build_prompt(
        search_question,
        context
    )


    # =====================================================
    # Generate Answer
    # =====================================================

    answer = llm_service.generate_response(
        prompt
    )

    answer = (
        answer.strip()
        if answer
        else ""
    )

    if not answer:
        answer = (
            "I don't know based on the provided documents."
        )


    # =====================================================
    # Prepare Sources
    # =====================================================

    sources = []

    for index, result in enumerate(results, start=1):

        sources.append(
            {
                "rank": index,
                "source": result.get(
                    "source"
                ),
                "document_name": result.get(
                    "document_name"
                ),
                "file_type": result.get(
                    "file_type"
                ),
                "chunk_id": result.get(
                    "chunk_id"
                ),
                "similarity": result.get(
                    "score"
                ),
                "keyword_score": result.get(
                    "keyword_score",
                    0.0
                ),
                "hybrid_score": result.get(
                    "hybrid_score",
                    result.get("score")
                ),
                "reranker_score": result.get(
                    "reranker_score",
                    result.get("score")
                ),
                "text": result.get(
                    "text",
                    ""
                )
            }
        )


    # =====================================================
    # Store Conversation
    # =====================================================

    conversation_memory.add_message(
        question,
        answer
    )


    # =====================================================
    # Return Result
    # =====================================================

    return {
        "answer": answer,
        "sources": sources,
        "search_question": search_question
    }


# =========================================================
# CLI ENTRY POINT
# =========================================================

def main():

    from embeddings import EmbeddingService
    from llm import LLMService
    from prompt_builder import PromptBuilder
    from query_rewriter import QueryRewriter
    from retriever import Retriever
    from vector_store import VectorStore


    # =====================================================
    # Initialize Services
    # =====================================================

    embedding_service = EmbeddingService()

    vector_store = VectorStore(
        dimension=384
    )

    retriever = Retriever(
        embedding_service,
        vector_store
    )

    llm_service = LLMService()

    query_rewriter = QueryRewriter(
        llm_service
    )

    prompt_builder = PromptBuilder()

    conversation_memory = ConversationMemory(
        max_messages=6
    )


    # =====================================================
    # Interactive CLI
    # =====================================================

    print(
        "\nEnterprise RAG Knowledge Base"
    )

    print(
        "Type 'exit' to stop."
    )


    try:

        while True:

            question = input(
                "\nQuestion: "
            ).strip()

            if question.lower() == "exit":
                break

            if not question:
                continue


            result = ask_question(
                question=question,
                conversation_memory=conversation_memory,
                query_rewriter=query_rewriter,
                retriever=retriever,
                prompt_builder=prompt_builder,
                llm_service=llm_service
            )


            print(
                "\nAnswer:"
            )

            print(
                result["answer"]
            )


            if result["sources"]:

                print(
                    "\nSources:"
                )

                for source in result["sources"]:

                    print(
                        f"- "
                        f"{source['document_name']} "
                        f"| Chunk "
                        f"{source['chunk_id']} "
                        f"| Score "
                        f"{source['similarity']:.4f}"
                    )

    finally:

        vector_store.close()


if __name__ == "__main__":
    main()