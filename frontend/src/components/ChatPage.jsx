import { Box, Typography } from "@mui/material";
import { useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";
import ChatBar from "./ChatBar";
import { useChat } from "../hooks/useChat";

const ChatPage = () => {
  const { messages, isStreaming, sendMessage } = useChat();
  const messagesEndRef = useRef(null);

  const hasMessages = messages.length > 0;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (msg) => {
    if (isStreaming) return;
    sendMessage(msg);
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        width: "100%",
        maxWidth: "100%",
        bgcolor: "#1e1e1e",
      }}
    >
      <Box
        sx={{
          flex: 1,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          justifyContent: hasMessages ? "flex-start" : "center",
          alignItems: "center",
          px: 2,
          py: 2,
        }}
      >
        {!hasMessages && (
          <Box sx={{ textAlign: "center", mb: 4 }}>
            <Typography
              variant="h4"
              sx={{ color: "#e0e0e0", fontWeight: 600, mb: 1 }}
            >
              Arch Helper
            </Typography>
            <Typography sx={{ color: "#888", fontSize: "1rem" }}>
              Ask anything about Arch Linux
            </Typography>
          </Box>
        )}

        {messages.map((msg, i) => (
          <ChatMessage key={i} role={msg.role} content={msg.content} />
        ))}

        {isStreaming &&
          messages.length > 0 &&
          messages[messages.length - 1].content === "" && (
            <Box sx={{ maxWidth: "48rem", width: "100%", mx: "auto", px: 2 }}>
              <Typography
                sx={{ color: "#888", fontSize: "0.85rem", fontStyle: "italic" }}
              >
                Thinking...
              </Typography>
            </Box>
          )}

        <div ref={messagesEndRef} />
      </Box>

      <Box
        sx={{
          borderTop: hasMessages ? "1px solid #333" : "none",
          p: 2,
          display: "flex",
          justifyContent: "center",
          bgcolor: "#1e1e1e",
        }}
      >
        <ChatBar onSend={handleSubmit} disabled={isStreaming} />
      </Box>
    </Box>
  );
};

export default ChatPage;
