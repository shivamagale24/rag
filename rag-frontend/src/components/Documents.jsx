function Documents({
  documents,
  loading,
  onDelete
}) {
  return (
    <div className="panel">
      <div className="section-header">
        <h2>Documents</h2>

        <span className="document-count">
          {documents.length}
        </span>
      </div>

      {loading ? (
        <p className="muted">
          Loading documents...
        </p>
      ) : documents.length === 0 ? (
        <div className="empty-documents">
          <div>📂</div>

          <p>No documents uploaded.</p>

          <small>
            Upload a document to start asking
            questions.
          </small>
        </div>
      ) : (
        <div className="documents">
          {documents.map((document) => (
            <div
              className="document"
              key={document.filename}
            >
              <div className="document-info">
                <span className="document-icon">
                  📄
                </span>

                <strong title={document.filename}>
                  {document.filename}
                </strong>
              </div>

              <button
                type="button"
                className="delete-button"
                onClick={() =>
                  onDelete(document.filename)
                }
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Documents;