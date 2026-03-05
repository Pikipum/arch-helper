import { Button, TextField, Box } from "@mui/material";
import { useNavigate } from "react-router";
import { useEffect, useState } from "react";

const formSx = {
  display: "flex",
  gap: "1rem",
  width: "min(40rem, 90vw)",
};

const inputSx = {
  flex: 1,
  "& .MuiOutlinedInput-root": {
    backgroundColor: "#2a2a2a",
    color: "#f5f5f5",
    borderRadius: "4px",
    "&:hover .MuiOutlinedInput-notchedOutline": { borderColor: "#666" },
    "&.Mui-focused .MuiOutlinedInput-notchedOutline": { borderColor: "#666" },
  },
  "& .MuiOutlinedInput-notchedOutline": {
    borderColor: "#444",
  },
  "& .MuiOutlinedInput-input::placeholder": {
    color: "#cfcfcf",
    opacity: 1,
  },
};

const buttonSx = {
  bgcolor: "primary.main",
  color: "#1e1e1e",
  fontWeight: "bold",
  py: 0,
  px: { xs: "1rem", sm: "2rem" },
  "&:hover": {
    bgcolor: "primary.dark",
  },
};

const SearchBar = () => {
  //const navigate = useNavigate();
  const [message, setMessage] = useState("");
  const [llmResponse, setLlmResponse] = useState("");

  const sendMessage = async (msg) => {
    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
        },
        body: JSON.stringify({ message: msg }),
      });

      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }

      const reader = response.body
        .pipeThrough(new TextDecoderStream())
        .getReader();

      let buffer = "";
      setLlmResponse("");

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          console.log("Stream done");
          break;
        }

        buffer += value;
        // Split on double-newline SSE boundaries
        const parts = buffer.split("\n\n");
        buffer = parts.pop(); // keep incomplete tail in buffer

        for (const part of parts) {
          const line = part.trim();
          if (!line) continue;
          if (line === "data: [DONE]") {
            console.log("[DONE] received");
            continue;
          }
          if (!line.startsWith("data: ")) continue;

          const payload = JSON.parse(line.slice(6));
          if (payload.type === "token") {
            setLlmResponse((prev) => prev + payload.content);
          }
        }
      }
    } catch (e) {
      console.error("execution error:", e);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log(event.target[0].value);
    sendMessage(event.target[0].value);
    //navigate(`/${region}/${encodeURIComponent(summoner.trim())}`);
  };

  return (
    <Box component="form" sx={formSx} onSubmit={(event) => handleSubmit(event)}>
      <TextField
        id="outlined-basic"
        variant="outlined"
        placeholder="Ask something..."
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        sx={inputSx}
      />
      <Button variant="contained" type="submit" sx={buttonSx}>
        Search
      </Button>
      {llmResponse}
    </Box>
  );
};

export default SearchBar;
