import { useState } from "react";
import { sendQuery } from "../api/queryApi";

export function useQuery() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const submitQuery = async (queryData) => {
    try {
      setLoading(true);
      setError(null);
      setResult(null);

      const response = await sendQuery(queryData);

      setResult(response);
      return response;
    } catch (err) {
      const errorMessage =
        err?.message ||
        "Something went wrong while processing your query.";

      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => {
    setError(null);
  };

  const clearResult = () => {
    setResult(null);
  };

  return {
    result,
    loading,
    error,
    submitQuery,
    clearError,
    clearResult,
  };
}