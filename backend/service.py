import json
from collections.abc import AsyncGenerator
from langchain_core.messages import AIMessageChunk
from rag import agent

async def chat_stream(message: str, history: list[dict]) -> AsyncGenerator[str, None]:
    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    # Stream agent events
    async for event, metadata in agent.astream(
        {"messages": messages},
        stream_mode="messages",
    ):
        # Only forward AI message chunks (skip human/tool echoes)
        if isinstance(event, AIMessageChunk) and event.content:
            payload = json.dumps({
                "type": "token",
                "content": event.content,
            })
            yield f"data: {payload}\n\n"

    yield "data: [DONE]\n\n"