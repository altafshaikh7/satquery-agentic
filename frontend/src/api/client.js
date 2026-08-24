const API_BASE_URL = "http://127.0.0.1:8000";

const apiClient = {
  async post(endpoint, data) {
    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      }
    );

    const responseData = await response
      .json()
      .catch(() => null);

    if (!response.ok) {
      const errorMessage =
        responseData?.detail ||
        responseData?.message ||
        `Request failed with status ${response.status}`;

      throw new Error(
        typeof errorMessage === "string"
          ? errorMessage
          : JSON.stringify(errorMessage)
      );
    }

    return {
      data: responseData,
    };
  },

  async upload(endpoint, file) {
    if (!file) {
      throw new Error("Please select an image file.");
    }

    const formData = new FormData();

    formData.append("file", file);

    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        method: "POST",
        body: formData,
      }
    );

    const responseData = await response
      .json()
      .catch(() => null);

    if (!response.ok) {
      const errorMessage =
        responseData?.detail ||
        responseData?.message ||
        `Upload failed with status ${response.status}`;

      throw new Error(
        typeof errorMessage === "string"
          ? errorMessage
          : JSON.stringify(errorMessage)
      );
    }

    return {
      data: responseData,
    };
  },
};

export default apiClient;