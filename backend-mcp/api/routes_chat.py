from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from agents.graph import invoke_graph
import json
import datetime
from typing import Any, AsyncGenerator

router = APIRouter()

class ChatRequest(BaseModel):
    persona: str
    session_id: str
    message: str
    event_id: str
    context: dict[str, Any]

@router.post("/chat")
async def chat_endpoint(request: Request, body: ChatRequest) -> EventSourceResponse:
    async def event_generator() -> AsyncGenerator[dict[str, str], None]:
        async for event in invoke_graph(body.persona, body.session_id, body.event_id, body.message):
            kind = event["event"]
            timestamp = datetime.datetime.utcnow().isoformat() + "Z"

            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    # Robustly ensure content is a string. Some models return lists 
                    # for tool calls or multimodal segments, which breaks string concatenation.
                    content = chunk.content
                    if isinstance(content, list):
                        # Join text parts if it's a list of dicts/segments
                        content = "".join([
                            str(c.get("text", "")) if isinstance(c, dict) else str(c) 
                            for c in content
                        ])
                    
                    yield {
                        "data": json.dumps({
                            "type": "token",
                            "content": str(content),
                            "timestamp": timestamp
                        })
                    }

            elif kind == "on_tool_start":
                yield {
                    "data": json.dumps({
                        "type": "tool_call",
                        "tool_used": event["name"],
                        "content": json.dumps(event["data"].get("input", {})),
                        "timestamp": timestamp
                    })
                }

        yield {
            "data": json.dumps({
                "type": "final",
                "content": "done",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            })
        }

    return EventSourceResponse(event_generator())
