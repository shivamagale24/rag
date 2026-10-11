function ChatHistory({
  sessions,
  currentSessionId,
  onSelect,
  onNewChat
}) {
  return (
    <div className="panel history-panel">
      <div className="section-header">
        <h2>Chat History</h2>

        <button
          type="button"
          className="history-new-button"
          onClick={onNewChat}
        >
          +
        </button>
      </div>

      {sessions.length === 0 ? (
        <div className="empty-history">
          <p>No previous chats.</p>

          <small>
            Your conversations will appear here.
          </small>
        </div>
      ) : (
        <div className="history-list">
          {sessions.map((session) => (
            <button
              type="button"
              key={session.id}
              className={`history-item ${
                session.id === currentSessionId
                  ? "active-history"
                  : ""
              }`}
              onClick={() => onSelect(session.id)}
            >
              <span className="history-icon">
                💬
              </span>

              <span className="history-content">
                <strong>
                  {session.title ||
                    "New conversation"}
                </strong>

                <small>
                  {session.messages.length} message
                  {session.messages.length !== 1
                    ? "s"
                    : ""}
                </small>
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default ChatHistory;