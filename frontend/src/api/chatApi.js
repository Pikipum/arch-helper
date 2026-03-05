const API_URL = "http://localhost:8000/api/chat";

/**
 *
 * @param {string} message  - The user message to send
 * @param {Array}  history  - Chat history array of { role, content }
 * @param {(token: string) => void} onToken - Called for each streamed token
 * @param {AbortSignal} [signal] - Optional abort signal
 */
export async function streamChat(message, history, onToken, signal) {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({ message, history }),
    signal,
  });

  if (!response.ok) {
    throw new Error(`Response status: ${response.status}`);
  }

  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += value;
    const parts = buffer.split("\n\n");
    buffer = parts.pop();

    for (const part of parts) {
      const line = part.trim();
      if (!line || line === "data: [DONE]") continue;
      if (!line.startsWith("data: ")) continue;

      const payload = JSON.parse(line.slice(6));
      if (payload.type === "token") {
        onToken(payload.content);
      }
    }
  }
}
