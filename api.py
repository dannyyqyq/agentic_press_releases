from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
import os
from src.nodes import app as graph_app 
from datetime import datetime
from fastapi.responses import HTMLResponse

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

    full_state = inputs.copy()

    print(f"\n🚀 Starting Workflow for Persona: {req.persona.upper()}...")
    print("-" * 60)

    # astream yields updates as they happen
    async for output in graph_app.astream(inputs):
        for node_name, state_update in output.items():
            full_state.update(state_update)
            
            # --- YOUR LOGGING LOGIC START ---
            print(f"\n[NODE COMPLETED: {node_name.upper()}]")

            if "retrieved_samples" in state_update:
                print(f"Found {len(state_update['retrieved_samples'])} reference samples.")

            if "style_guide" in state_update:
                print("\n--- STYLE DNA EXTRACTED ---")
                print(state_update["style_guide"])
                print("-" * 30)

            if "taylor_swift_tweet_draft" in state_update and state_update["taylor_swift_tweet_draft"]:
                print(f"\n--- NEW TAYLOR SWIFT DRAFT ---\n{state_update['taylor_swift_tweet_draft']}")

            if "bbc_article_draft" in state_update and state_update["bbc_article_draft"]:
                print(f"\n--- NEW BBC DRAFT ---\n{state_update['bbc_article_draft']}")

            if "feedback_history" in state_update and state_update["feedback_history"]:
                print(f"\nCRITIC FEEDBACK:\n{state_update['feedback_history'][-1]}")

            if "revision_count" in state_update:
                print(f"Revision count: {state_update['revision_count']}")

            if "final_approval" in state_update:
                print(f"Final approval: {state_update['final_approval']}")

            print("\n" + "=" * 60 + "\n")

    # Extract final content for the API response
    content = (
        full_state.get("bbc_article_draft") 
        if req.persona == "bbc" 
        else full_state.get("taylor_swift_tweet_draft")
    )

    return Response(
        content=content or "[No content generated]",
        revision_count=full_state.get("revision_count", 0),
        approved=full_state.get("final_approval", False)
    )
    
    
@app.get("/privacy", response_class=HTMLResponse)
async def privacy_policy():
    return """
    <html>
        <head><title>Privacy Policy</title></head>
        <body>
            <h1>Privacy Policy for Style Mimic Agent</h1>
            <p><strong>Effective Date:</strong> December 2025</p>
            <p>This AI agent is a personal project created for academic/demonstration purposes. 
            It does not collect, store, or share any personal data from users.</p>
            <ul>
                <li><strong>Data Collection:</strong> No personally identifiable information (PII) is collected.</li>
                <li><strong>Data Usage:</strong> Inputs are processed in real-time to generate style-mimicked content and are not stored on our servers.</li>
                <li><strong>Third Parties:</strong> Data is processed via OpenAI APIs in accordance with their standard privacy terms.</li>
            </ul>
            <p>For questions, please contact the developer through the project repository.</p>
        </body>
    </html>
    """