function Sources({ sources }) {
  const uniqueSources = (sources || []).filter(
    (source, index, array) =>
      index ===
      array.findIndex(
        (item) =>
          item.source === source.source &&
          item.chunk_id === source.chunk_id
      )
  );

  if (uniqueSources.length === 0) {
    return (
      <div className="sources-empty">
        <div className="sources-empty-icon">
          📚
        </div>

        <p>No relevant sources found.</p>

        <small>
          Sources will appear here when the RAG
          system retrieves relevant document chunks.
        </small>
      </div>
    );
  }

  return (
    <div className="sources-section">
      <div className="sources-title">
        <div>
          <h3>Retrieved Sources</h3>

          <p>
            Sources are ordered by reranker relevance.
          </p>
        </div>

        <span className="source-count">
          {uniqueSources.length}
        </span>
      </div>

      <div className="sources-list">
        {uniqueSources.map((source, index) => (
          <div
            className="source-card"
            key={`${source.source}-${source.chunk_id}-${index}`}
          >
            <div className="source-header">
              <div className="source-document">
                <span className="source-rank">
                  #{source.rank || index + 1}
                </span>

                <div>
                  <strong title={source.source}>
                    {source.source}
                  </strong>

                  <span className="source-chunk">
                    Chunk {source.chunk_id ?? "N/A"}
                  </span>
                </div>
              </div>
            </div>

            {source.text && (
              <div className="source-preview">
                <div className="source-preview-title">
                  Retrieved text
                </div>

                <p>{source.text}</p>
              </div>
            )}

            <details className="source-details">
              <summary>
                Technical details
              </summary>

              <div className="source-details-grid">
                <div>
                  <span>Vector similarity</span>

                  <strong>
                    {typeof source.similarity ===
                    "number"
                      ? source.similarity.toFixed(3)
                      : "N/A"}
                  </strong>
                </div>

                <div>
                  <span>Reranker score</span>

                  <strong>
                    {typeof source.reranker_score ===
                    "number"
                      ? source.reranker_score.toFixed(3)
                      : "N/A"}
                  </strong>
                </div>

                <div>
                  <span>Chunk</span>

                  <strong>
                    {source.chunk_id ?? "N/A"}
                  </strong>
                </div>
              </div>
            </details>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Sources;