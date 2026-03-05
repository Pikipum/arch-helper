import { TextField, Box, IconButton } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { useState } from "react";

const inputSx = {
  "& .MuiOutlinedInput-root": {
    backgroundColor: "#2a2a2a",
    color: "#f5f5f5",
    borderRadius: "24px",
    px: 1,
    "&:hover .MuiOutlinedInput-notchedOutline": { borderColor: "#555" },
    "&.Mui-focused .MuiOutlinedInput-notchedOutline": { borderColor: "#666" },
  },
  "& .MuiOutlinedInput-notchedOutline": {
    borderColor: "#444",
  },
  "& .MuiOutlinedInput-input::placeholder": {
    color: "#999",
    opacity: 1,
  },
};

const ChatBar = ({ onSend, disabled = false }) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    setInput("");
    onSend(trimmed);
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        display: "flex",
        gap: "0.75rem",
        width: "min(48rem, 90vw)",
        alignItems: "center",
      }}
    >
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Ask something about Arch Linux..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={disabled}
        autoFocus
        sx={inputSx}
      />
      <IconButton
        type="submit"
        disabled={!input.trim() || disabled}
        sx={{
          bgcolor: input.trim() ? "primary.main" : "#333",
          color: input.trim() ? "#1e1e1e" : "#666",
          width: 44,
          height: 44,
          "&:hover": {
            bgcolor: input.trim() ? "primary.dark" : "#333",
          },
          "&.Mui-disabled": {
            bgcolor: "#333",
            color: "#666",
          },
        }}
      >
        <SendIcon fontSize="small" />
      </IconButton>
    </Box>
  );
};

export default ChatBar;
