const API_BASE_URL = "http://127.0.0.1:8000";

const apiClient = {
  async post(endpoint, data) {
    console.log(
      "ACTUAL REQUEST BODY:",
      JSON.stringify(data, null, 2)
    );

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

    console.log(
      "API Response Status:",
      response.status
    );

    console.log(
      "API Response:",
      responseData
    );

    if (!response.ok) {
      let errorMessage =
        `Request failed with status ${response.status}`;

      if (typeof responseData?.detail === "string") {
        errorMessage = responseData.detail;

      } else if (Array.isArray(responseData?.detail)) {
        errorMessage = responseData.detail
          .map((error) => {
            const field =
              error.loc?.join(" → ") || "Validation";

            return `${field}: ${error.msg}`;
          })
          .join("\n");

      } else if (
        typeof responseData?.message === "string"
      ) {
        errorMessage = responseData.message;

      } else if (responseData?.detail) {
        errorMessage = JSON.stringify(
          responseData.detail,
          null,
          2
        );
      }

      throw new Error(errorMessage);
    }

    return {
      data: responseData,
    };
  },
};

export default apiClient;