import { useState } from "react";
import { streamChat } from "../api/chatApi";

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);

  const sendMessage = async (msg) => {
    const userMsg = { role: "user", content: msg };
    const assistantMsg = { role: "assistant", content: "" };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setIsStreaming(true);

    try {
      const history = [...messages, userMsg].map(({ role, content }) => ({
        role,
        content,
      }));

      await streamChat(msg, history, (token) => {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          updated[updated.length - 1] = {
            ...last,
            content: last.content + token,
          };
          return updated;
        });
      });
    } catch (e) {
      console.error("Stream error:", e);
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
        };
        return updated;
      });
    } finally {
      setIsStreaming(false);
    }
  };

  return { messages, isStreaming, sendMessage };
}
