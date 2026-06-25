const API_URL = "http://127.0.0.1:8000/api/query";

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