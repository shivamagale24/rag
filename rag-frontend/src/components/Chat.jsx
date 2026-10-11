import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

function formatTime(timestamp) {
  if (!timestamp) {
    return "";
  }

  return new Date(timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit"
  });
}

function Chat({
  messages,
  question,
  loading,
  onQuestionChange,
  onSend,
  onKeyDown,
  onClear,
  canClear,
  onExampleQuestion
}) {
  const messagesEndRef = useRef(null);
  const [copiedIndex, setCopiedIndex] = useState(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });
  }, [messages, loading]);

  async function handleCopy(content, index) {
    try {
      await navigator.clipboard.writeText(content);

      setCopiedIndex(index);

      setTimeout(() => {
        setCopiedIndex(null);
      }, 1500);
    } catch {
      setCopiedIndex(null);
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div>
          <h2>Chat</h2>
          <p>
            Ask questions about your uploaded documents.
          </p>
        </div>

        <button
          type="button"
          className="clear-button"
          onClick={onClear}
          disabled={!canClear}
        >
          Clear
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && !loading ? (
          <div className="empty-chat">
            <div className="empty-chat-icon">
              💬
            </div>

            <h3>Start a conversation</h3>

            <p>
              Ask a question about the documents in your
              knowledge base.
            </p>

            <div className="example-questions">
              <button
                type="button"
                onClick={() =>
                  onExampleQuestion(
                    "What documents are available?"
                  )
                }
              >
                What documents are available?
              </button>

              <button
                type="button"
                onClick={() =>
                  onExampleQuestion(
                    "What information is available in the documents?"
                  )
                }
              >
                What information is available?
              </button>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div
                key={`${message.timestamp || index}-${index}`}
                className={`message ${
                  message.role === "user"
                    ? "user-message"
                    : "assistant-message"
                }`}
              >
                <div className="message-header">
                  <strong>
                    {message.role === "user"
                      ? "You"
                      : "Assistant"}
                  </strong>

                  {message.timestamp && (
                    <span>
                      {formatTime(message.timestamp)}
                    </span>
                  )}
                </div>

                <div className="message-content">
                  {message.role === "assistant" ? (
                    <ReactMarkdown>
                      {message.content}
                    </ReactMarkdown>
                  ) : (
                    <p>{message.content}</p>
                  )}
                </div>

                {message.role === "assistant" && (
                  <button
                    type="button"
                    className="copy-button"
                    onClick={() =>
                      handleCopy(
                        message.content,
                        index
                      )
                    }
                  >
                    {copiedIndex === index
                      ? "Copied"
                      : "Copy"}
                  </button>
                )}
              </div>
            ))}

            {loading && (
              <div className="message assistant-message">
                <div className="message-header">
                  <strong>Assistant</strong>
                </div>

                <div className="thinking">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <div className="chat-input-area">
        <textarea
          value={question}
          onChange={(event) =>
            onQuestionChange(event.target.value)
          }
          onKeyDown={onKeyDown}
          placeholder="Ask a question about your documents..."
          disabled={loading}
          rows={3}
        />

        <div className="chat-input-footer">
          <small>
            Press Enter to send. Shift + Enter for a new
            line.
          </small>

          <button
            type="button"
            className="send-button"
            onClick={onSend}
            disabled={!question.trim() || loading}
          >
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chat;