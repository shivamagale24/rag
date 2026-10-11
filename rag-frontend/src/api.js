const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

async function parseError(response, fallbackMessage) {
  try {
    const data = await response.json();

    if (data?.detail) {
      return data.detail;
    }
  } catch {
    // Use fallback message.
  }

  return fallbackMessage;
}

export async function askQuestion(sessionId, question) {
  const response = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      session_id: sessionId,
      question
    })
  });

  if (!response.ok) {
    throw new Error(
      await parseError(
        response,
        "Failed to get answer."
      )
    );
  }

  return response.json();
}

export async function clearConversation(sessionId) {
  const response = await fetch(`${API_URL}/clear`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      session_id: sessionId
    })
  });

  if (!response.ok) {
    throw new Error(
      await parseError(
        response,
        "Failed to clear conversation."
      )
    );
  }

  return response.json();
}

export async function getDocuments() {
  const response = await fetch(
    `${API_URL}/documents`
  );

  if (!response.ok) {
    throw new Error(
      await parseError(
        response,
        "Failed to load documents."
      )
    );
  }

  return response.json();
}

export function uploadDocument(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.open("POST", `${API_URL}/upload`);

    xhr.upload.addEventListener(
      "progress",
      (event) => {
        if (!event.lengthComputable) {
          return;
        }

        const progress = Math.round(
          (event.loaded / event.total) * 100
        );

        onProgress?.(progress);
      }
    );

    xhr.addEventListener("load", () => {
      let data = {};

      try {
        data = JSON.parse(xhr.responseText);
      } catch {
        data = {};
      }

      if (
        xhr.status >= 200 &&
        xhr.status < 300
      ) {
        onProgress?.(100);
        resolve(data);
        return;
      }

      reject(
        new Error(
          data?.detail ||
            "Failed to upload file."
        )
      );
    });

    xhr.addEventListener("error", () => {
      reject(
        new Error(
          "Network error while uploading the document."
        )
      );
    });

    xhr.addEventListener("abort", () => {
      reject(
        new Error(
          "Document upload was cancelled."
        )
      );
    });

    const formData = new FormData();
    formData.append("file", file);

    xhr.send(formData);
  });
}

export async function deleteDocument(filename) {
  const response = await fetch(
    `${API_URL}/documents/${encodeURIComponent(filename)}`,
    {
      method: "DELETE"
    }
  );

  if (!response.ok) {
    throw new Error(
      await parseError(
        response,
        "Failed to delete document."
      )
    );
  }

  return response.json();
}