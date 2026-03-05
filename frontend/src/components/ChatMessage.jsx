import { Box, Typography } from "@mui/material";
import PersonIcon from "@mui/icons-material/Person";
import SmartToyIcon from "@mui/icons-material/SmartToy";

const messageBubbleSx = (isUser) => ({
  display: "flex",
  gap: "0.75rem",
  alignItems: "flex-start",
  maxWidth: "48rem",
  width: "100%",
  mx: "auto",
  py: 1.5,
  px: 2,
});

const iconSx = (isUser) => ({
  width: 32,
  height: 32,
  borderRadius: "50%",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  flexShrink: 0,
  bgcolor: isUser ? "#5c6bc0" : "#2e7d32",
  color: "#fff",
  mt: 0.25,
});

const ChatMessage = ({ role, content }) => {
  const isUser = role === "user";

  return (
    <Box sx={messageBubbleSx(isUser)}>
      <Box sx={iconSx(isUser)}>
        {isUser ? (
          <PersonIcon fontSize="small" />
        ) : (
          <SmartToyIcon fontSize="small" />
        )}
      </Box>
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Typography
          variant="subtitle2"
          sx={{ color: "#aaa", mb: 0.25, fontSize: "0.75rem" }}
        >
          {isUser ? "You" : "Arch Helper"}
        </Typography>
        <Typography
          sx={{
            color: "#e0e0e0",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            lineHeight: 1.6,
            fontSize: "0.95rem",
          }}
        >
          {content}
        </Typography>
      </Box>
    </Box>
  );
};

export default ChatMessage;
