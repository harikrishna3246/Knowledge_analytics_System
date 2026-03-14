// This module centralizes API base URL configuration for the frontend.
// It supports overriding via REACT_APP_API_BASE_URL (e.g., for local dev or production).
// If REACT_APP_API_BASE_URL is not set, we default to a relative path so that
// requests go to the same origin as the frontend (works well when the backend
// is served from the same host).

const API_BASE_URL = (process.env.REACT_APP_API_BASE_URL || "").replace(/\/$/, "");

export const apiUrl = (path) => `${API_BASE_URL}${path}`;

export default API_BASE_URL;
