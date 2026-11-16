// Local dev talks to the backend on port 8000; the deployed build calls
// /api on its own origin. VITE_API_BASE_URL overrides both.
const API_BASE =
  import.meta.env.VITE_API_BASE_URL ??
  (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");
const API_URL = `${API_BASE.replace(/\/$/, "")}/api/query`;

export async function askQuestion(question) {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error("Backend request failed");
  }

  return await response.json();
}