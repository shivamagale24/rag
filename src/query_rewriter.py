class QueryRewriter:

    def __init__(self, llm_service):
        self.llm_service = llm_service

    def rewrite(
        self,
        question,
        conversation_history
    ):
        if not conversation_history:
            return question

        history_text = []

        for message in conversation_history[-6:]:
            history_text.append(
                f"User: {message.get('question', '')}"
            )
            history_text.append(
                f"Assistant: {message.get('answer', '')}"
            )

        history = "\n".join(history_text)

        prompt = f"""
You are a query rewriting component for an enterprise
knowledge base.

Rewrite the latest user question into a standalone,
clear search question that can be used to retrieve
relevant information from the knowledge base.

Conversation history:
{history}

Latest user question:
{question}

Rules:
- Return only the rewritten search question.
- Preserve the user's original topic and intent.
- Resolve pronouns and references using the conversation.
- Do not invent information.
- Make the question specific enough for semantic and
  keyword retrieval.
- If the latest question is already standalone,
  keep it unchanged.

Example:
Previous question:
"What programming languages are mentioned in the resume?"

Previous answer:
"Python and Java are mentioned."

Latest question:
"What about the other skills?"

Rewritten question:
"What other skills are mentioned in the resume besides
Python and Java?"
"""

        try:
            rewritten_question = (
                self.llm_service.generate_response(
                    prompt
                )
            )

            if rewritten_question:
                return rewritten_question.strip()

        except Exception:
            pass

        return question