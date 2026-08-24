import apiClient from "./client";

export async function sendQuery(queryData) {
  const response = await apiClient.post(
    "/query/",
    queryData
  );

  return response.data;
}