function Upload({
  selectedFile,
  uploadMessage,
  uploading,
  uploadProgress,
  onFileChange,
  onUpload
}) {
  return (
    <div className="panel">
      <div className="section-header">
        <h2>Upload Document</h2>
      </div>

      <div className="upload-content">
        <input
          type="file"
          id="document-upload"
          accept=".pdf,.txt,.docx"
          onChange={onFileChange}
          disabled={uploading}
        />

        <label
          htmlFor="document-upload"
          className="file-label"
        >
          Choose PDF, TXT, or DOCX
        </label>

        {selectedFile && (
          <div className="selected-file">
            <strong>
              {selectedFile.name}
            </strong>

            <span>
              {(selectedFile.size / (1024 * 1024)).toFixed(
                2
              )}{" "}
              MB
            </span>
          </div>
        )}

        {uploading && (
          <div className="upload-progress">
            <div className="progress-header">
              <span>
                {uploadProgress < 100
                  ? "Uploading and indexing..."
                  : "Processing complete"}
              </span>

              <span>{uploadProgress}%</span>
            </div>

            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${uploadProgress}%`
                }}
              />
            </div>
          </div>
        )}

        <button
          type="button"
          className="upload-button"
          onClick={onUpload}
          disabled={!selectedFile || uploading}
        >
          {uploading
            ? "Uploading..."
            : "Upload Document"}
        </button>

        {uploadMessage && (
          <p className="success-message">
            {uploadMessage}
          </p>
        )}

        <small className="upload-help">
          Supported formats: PDF, TXT, DOCX
          <br />
          Maximum file size: 10 MB
        </small>
      </div>
    </div>
  );
}

export default Upload;