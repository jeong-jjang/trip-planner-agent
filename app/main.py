"""

pip install -r requirements.txt
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage, AIMessage
from app.graph.workflow import graph

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

from fastapi.responses import StreamingResponse
import json

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    # 1. LangChain 메시지 변환
    lc_messages = []
    for msg in request.messages:
        if msg.role == "human":
            lc_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "ai":
            lc_messages.append(AIMessage(content=msg.content))

    # 2. Generator 함수 정의
    def generate():
        try:
            for step in graph.stream({"messages": lc_messages}):
                if "__end__" not in step:
                    # 직렬화
                    for k, v in step.items():
                        if "messages" in v:
                            v["messages"] = [
                                {"role": type(m).__name__.replace("Message", "").lower(), "content": m.content}
                                for m in v["messages"]
                            ]
                    # yield: JSON 한 줄씩 보내기 (NDJSON 스타일)
                    yield json.dumps(step, ensure_ascii=False) + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}, ensure_ascii=False) + "\n"

    # 3. StreamingResponse 반환
    return StreamingResponse(generate(), media_type="application/json")

