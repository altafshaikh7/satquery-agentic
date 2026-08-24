export const API_BASE_URL = "http://127.0.0.1:8000";

export const API_ENDPOINTS = {
  HEALTH: "/health",
  QUERY: "/api/query",
  TRACES: "/api/traces",
};

export const EXAMPLE_QUERIES = [
  "What is visible in this satellite image?",
  "Detect changes between the before and after images.",
  "Analyze vegetation health using NDVI.",
  "Describe the land use in the selected region.",
];

export const QUERY_PLACEHOLDER =
  "Ask a question about satellite imagery, land changes, vegetation, or a location...";