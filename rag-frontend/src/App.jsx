import { useEffect, useState } from "react";
import "./App.css";

import {
  askQuestion,
  clearConversation,
  getDocuments,
  uploadDocument,
  deleteDocument
} from "./api";

import Chat from "./components/Chat";
import Upload from "./components/Upload";
import Documents from "./components/Documents";
import Sources from "./components/Sources";
import ChatHistory from "./components/ChatHistory";

const ALLOWED_TYPES = [
  "application/pdf",
  "text/plain",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
];

const ALLOWED_EXTENSIONS = [".pdf", ".txt", ".docx"];

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const STORAGE_KEY = "enterprise-rag-chat-history";

function createSession() {
  return {
    id: crypto.randomUUID(),
    title: "New conversation",
    messages: [],
    sources: [],
    createdAt: new Date().toISOString()
  };
}

function App() {
  const [sessions, setSessions] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);

      if (!stored) {
        return [];
      }

      const parsed = JSON.parse(stored);

      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  });

  const [currentSessionId, setCurrentSessionId] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);

      if (!stored) {
        return crypto.randomUUID();
      }

      const parsed = JSON.parse(stored);

      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed[0].id;
      }
    } catch {
      // Create a new session below.
    }

    return crypto.randomUUID();
  });

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadMessage, setUploadMessage] = useState("");

  const currentSession =
    sessions.find(
      (session) => session.id === currentSessionId
    ) || null;

  useEffect(() => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(sessions)
    );
  }, [sessions]);

  useEffect(() => {
    loadDocuments();
  }, []);

  async function loadDocuments() {
    setDocumentsLoading(true);

    try {
      const data = await getDocuments();

      setDocuments(data.documents || []);
    } catch (err) {
      setError(err.message || "Failed to load documents.");
    } finally {
      setDocumentsLoading(false);
    }
  }

  function updateCurrentSession(updater) {
    setSessions((previousSessions) =>
      previousSessions.map((session) =>
        session.id === currentSessionId
          ? updater(session)
          : session
      )
    );
  }

  async function handleSendQuestion() {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setError("");
    setLoading(true);

    const userMessage = {
      role: "user",
      content: trimmedQuestion,
      timestamp: new Date().toISOString()
    };

    updateCurrentSession((session) => {
      const messages = [
        ...session.messages,
        userMessage
      ];

      return {
        ...session,
        title:
          session.messages.length === 0
            ? trimmedQuestion.slice(0, 50)
            : session.title,
        messages
      };
    });

    setQuestion("");

    try {
      const data = await askQuestion(
        currentSessionId,
        trimmedQuestion
      );

      const assistantMessage = {
        role: "assistant",
        content: data.answer || "",
        timestamp: new Date().toISOString()
      };

      updateCurrentSession((session) => ({
        ...session,
        messages: [
          ...session.messages,
          assistantMessage
        ],
        sources: data.sources || []
      }));
    } catch (err) {
      setError(
        err.message || "Failed to get an answer."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleQuestionKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendQuestion();
    }
  }

  async function handleClearConversation() {
    if (!currentSession) {
      return;
    }

    setError("");

    try {
      await clearConversation(currentSessionId);

      updateCurrentSession((session) => ({
        ...session,
        messages: [],
        sources: [],
        title: "New conversation"
      }));
    } catch (err) {
      setError(
        err.message || "Failed to clear conversation."
      );
    }
  }

  function handleNewChat() {
    const newSession = createSession();

    setSessions((previousSessions) => [
      newSession,
      ...previousSessions
    ]);

    setCurrentSessionId(newSession.id);
    setQuestion("");
    setError("");
  }

  function handleSelectChat(sessionId) {
    setCurrentSessionId(sessionId);
    setQuestion("");
    setError("");
  }

  function handleFileChange(event) {
    const file = event.target.files?.[0];

    setUploadMessage("");
    setError("");
    setUploadProgress(0);

    if (!file) {
      setSelectedFile(null);
      return;
    }

    const extension =
      "." +
      file.name
        .split(".")
        .pop()
        .toLowerCase();

    if (
      !ALLOWED_EXTENSIONS.includes(extension) ||
      !ALLOWED_TYPES.includes(file.type)
    ) {
      setSelectedFile(null);
      setError(
        "Only PDF, TXT, and DOCX files are supported."
      );
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setSelectedFile(null);
      setError("Maximum file size is 10 MB.");
      return;
    }

    setSelectedFile(file);
  }

  async function handleUpload() {
    if (!selectedFile || uploading) {
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setUploadMessage("");
    setError("");

    try {
      const data = await uploadDocument(
        selectedFile,
        (progress) => {
          setUploadProgress(progress);
        }
      );

      setUploadMessage(
        data.message || "Document uploaded successfully."
      );

      setSelectedFile(null);
      setUploadProgress(100);

      await loadDocuments();
    } catch (err) {
      setError(
        err.message || "Failed to upload document."
      );
      setUploadProgress(0);
    } finally {
      setUploading(false);
    }
  }

  async function handleDeleteDocument(filename) {
    const confirmed = window.confirm(
      `Delete "${filename}"?`
    );

    if (!confirmed) {
      return;
    }

    setError("");

    try {
      await deleteDocument(filename);

      await loadDocuments();
    } catch (err) {
      setError(
        err.message || "Failed to delete document."
      );
    }
  }

  function handleExampleQuestion(exampleQuestion) {
    setQuestion(exampleQuestion);
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Enterprise RAG Knowledge Base</h1>
          <p>
            Ask questions about your uploaded documents.
          </p>
        </div>
      </header>

      <div className="app-layout">
        <aside className="sidebar">
          <Upload
            selectedFile={selectedFile}
            uploadMessage={uploadMessage}
            uploading={uploading}
            uploadProgress={uploadProgress}
            onFileChange={handleFileChange}
            onUpload={handleUpload}
          />

          <Documents
            documents={documents}
            loading={documentsLoading}
            onDelete={handleDeleteDocument}
          />

          <ChatHistory
            sessions={sessions}
            currentSessionId={currentSessionId}
            onSelect={handleSelectChat}
            onNewChat={handleNewChat}
          />
        </aside>

        <main className="main-content">
          <div className="session-banner">
            <div>
              <span>Current conversation</span>
              <strong>
                {currentSession?.title ||
                  "New conversation"}
              </strong>
            </div>

            <span className="session-id">
              Session: {currentSessionId}
            </span>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <Chat
            messages={
              currentSession?.messages || []
            }
            question={question}
            loading={loading}
            onQuestionChange={setQuestion}
            onSend={handleSendQuestion}
            onKeyDown={handleQuestionKeyDown}
            onClear={handleClearConversation}
            canClear={
              Boolean(
                currentSession?.messages?.length
              ) && !loading
            }
            onExampleQuestion={
              handleExampleQuestion
            }
          />

          <Sources
            sources={
              currentSession?.sources || []
            }
          />
        </main>
      </div>
    </div>
  );
}

export default App;