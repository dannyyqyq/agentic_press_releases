from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
import os
from src.nodes import app as graph_app  # renamed to avoid conflict with FastAPI app
from datetime import datetime

# Simple uptime tracker
start_time = datetime.now()

# Load API Key before any other logic
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="Style Mimic Agent")

class Request(BaseModel):
    topic: str
    persona: Literal["bbc", "taylor_swift"]

class Response(BaseModel):
    content: str
    revision_count: int
    approved: bool

@app.get("/")
def read_root():
    return {"Message": "Welcome to mimic model!"}

@app.get("/health")
async def health_check():
    """
    Standard health check for deployment platforms and monitoring tools.
    """
    uptime = datetime.now() - start_time
    return {
        "status": "healthy",
        "uptime": str(uptime),
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "persona_agents": ["bbc", "taylor_swift"]
    }
    
@app.post("/generate", response_model=Response)
async def generate(req: Request):
    inputs = {
        "topic": req.topic,
        "selected_persona": req.persona,
        "retrieved_samples": [], "style_guide": "", "category": "",
        "bbc_article_draft": "", "taylor_swift_tweet_draft": "",
        "feedback_history": [], "revision_count": 0, "final_approval": False
    }

    # We use a dictionary to keep track of the accumulated state
    full_state = inputs.copy()

    # astream yields partial updates. We merge them into full_state.
    async for output in graph_app.astream(inputs):
        for node_name, state_update in output.items():
            full_state.update(state_update)

    # Extract the correct content based on persona
    if req.persona == "bbc":
        content = full_state.get("bbc_article_draft")
    else:
        content = full_state.get("taylor_swift_tweet_draft")

    return Response(
        content=content or "[No content generated]",
        revision_count=full_state.get("revision_count", 0),
        approved=full_state.get("final_approval", False)
    )