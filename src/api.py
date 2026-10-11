import os
import sys

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.append(
    os.path.dirname(os.path.abspath(__file__))
)

from embeddings import EmbeddingService
from indexer import index_document
from main import ask_question
from llm import LLMService
from prompt_builder import PromptBuilder
from query_rewriter import QueryRewriter
from retriever import Retriever
from vector_store import VectorStore


DOCUMENT_FOLDER = "data/documents"


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


app = FastAPI(
    title="Enterprise RAG Knowledge Base API",
    description="Backend API for the Enterprise RAG system",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class QuestionRequest(BaseModel):
    session_id: str
    question: str


class ClearRequest(BaseModel):
    session_id: str


conversation_sessions = {}


def get_conversation_memory(session_id):
    if session_id not in conversation_sessions:
        from conversation import ConversationMemory

        conversation_sessions[session_id] = (
            ConversationMemory(max_messages=6)
        )

    return conversation_sessions[session_id]


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/ask")
def ask(request: QuestionRequest):
    session_id = request.session_id.strip()
    question = request.question.strip()

    if not session_id:
        raise HTTPException(
            status_code=400,
            detail="Session ID is required."
        )

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question is required."
        )

    conversation_memory = (
        get_conversation_memory(session_id)
    )

    result = ask_question(
        question=question,
        conversation_memory=conversation_memory,
        query_rewriter=query_rewriter,
        retriever=retriever,
        prompt_builder=prompt_builder,
        llm_service=llm_service
    )

    return {
        "session_id": session_id,
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"]
    }


@app.post("/clear")
def clear_conversation(
    request: ClearRequest
):
    session_id = request.session_id.strip()

    if not session_id:
        raise HTTPException(
            status_code=400,
            detail="Session ID is required."
        )

    if session_id in conversation_sessions:
        conversation_sessions[
            session_id
        ].clear()

    return {
        "message": "Conversation cleared successfully.",
        "session_id": session_id
    }


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    filename = file.filename
    extension = os.path.splitext(
        filename
    )[1].lower()

    allowed_extensions = {
        ".pdf",
        ".txt",
        ".docx"
    }

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, and DOCX files are supported."
        )

    os.makedirs(
        DOCUMENT_FOLDER,
        exist_ok=True
    )

    file_path = os.path.join(
        DOCUMENT_FOLDER,
        filename
    )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    with open(file_path, "wb") as output_file:
        output_file.write(content)

    try:
        result = index_document(
            file_path,
            vector_store
        )
    except Exception as exc:
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail=f"Failed to index document: {exc}"
        ) from exc

    return {
        "message": "Document uploaded and indexed successfully.",
        "filename": filename,
        "chunks": result["chunks"]
    }


@app.get("/documents")
def get_documents():
    os.makedirs(
        DOCUMENT_FOLDER,
        exist_ok=True
    )

    documents = []

    for filename in sorted(
        os.listdir(DOCUMENT_FOLDER)
    ):
        file_path = os.path.join(
            DOCUMENT_FOLDER,
            filename
        )

        if os.path.isfile(file_path):
            documents.append(
                {
                    "filename": filename
                }
            )

    return {
        "documents": documents
    }


@app.delete("/documents/{filename}")
def delete_document(filename: str):
    file_path = os.path.join(
        DOCUMENT_FOLDER,
        filename
    )

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    try:
        vector_store.delete_document(
            filename
        )

        os.remove(file_path)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {exc}"
        ) from exc

    return {
        "message": "Document deleted successfully.",
        "filename": filename
    }