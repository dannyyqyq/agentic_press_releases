from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
from src.nodes import app  # your compiled graph

app = FastAPI(title="Style Mimic Agent")

class Request(BaseModel):
    topic: str
    persona: Literal["bbc", "taylor_swift"]

class Response(BaseModel):
    content: str
    revision_count: int
    approved: bool

@app.post("/generate")
async def generate(req: Request):
    inputs = {
        "topic": req.topic,
        "selected_persona": req.persona,
        "retrieved_samples": [], "style_guide": "", "category": "",
        "bbc_article_draft": "", "taylor_swift_tweet_draft": "",
        "feedback_history": [], "revision_count": 0, "final_approval": False
    }

    final_state = None
    async for output in app.astream(inputs):
        final_state = list(output.values())[-1]  # latest state

    content = (
        final_state.get("bbc_article_draft") 
        if req.persona == "bbc" 
        else final_state.get("taylor_swift_tweet_draft", "")
    )

    return Response(
        content=content or "[No content generated]",
        revision_count=final_state.get("revision_count", 0),
        approved=final_state.get("final_approval", False)
    )