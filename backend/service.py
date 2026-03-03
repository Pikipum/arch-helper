import json
from collections.abc import AsyncGenerator
from rag import agent

async def chat_stream(message: str, history: list[dict]) -> AsyncGenerator[str, None]:
    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    # Stream agent events
    for event in agent.stream(
        {"messages": messages},
        stream_mode="values",
    ):
        last = event["messages"][-1]

        # Only forward AI messages (skip human/tool echoes)
        if last.type == "ai" and last.content:
            payload = json.dumps({
                "type": "token",
                "content": last.content,
            })
            yield f"data: {payload}\n\n"

    yield "data: [DONE]\n\n"