import json
from collections.abc import AsyncGenerator
from langchain_core.messages import AIMessageChunk
from rag import agent


async def chat_stream(message: str, history: list[dict]) -> AsyncGenerator[str, None]:
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]
    messages.append({"role": "user", "content": message})

    async for event, metadata in agent.astream(
        {"messages": messages, "query": "", "docs": [], "good_docs": [], "context": ""},
        stream_mode="messages",
    ):
        if isinstance(event, AIMessageChunk) and event.content:
            payload = json.dumps({"type": "token", "content": event.content})
            yield f"data: {payload}\n\n"

    yield "data: [DONE]\n\n"