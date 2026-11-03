// Browser requests use the page's origin; nginx/Next.js proxies /api to the backend.
// An absolute URL breaks www/local access through CORS and cross-origin cookies.
export const API_URL = "/api";

export const API_INTERNAL_URL =
  process.env.API_INTERNAL_URL ?? "http://backend:8000/api";
