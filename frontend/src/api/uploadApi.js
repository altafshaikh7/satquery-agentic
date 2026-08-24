import apiClient from "./client";

export async function uploadImage(file) {
  const response = await apiClient.upload(
    "/upload/",
    file
  );

  return response.data;
}