import os
from dotenv import load_dotenv
load_dotenv()
from src.nodes import app
from src.logger import logging
from typing import Literal
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def mimic_model(topic: str, selected_persona: Literal["bbc", "taylor_swift"]):
    inputs = {
        "topic": topic,
        "selected_persona": selected_persona,
        "retrieved_samples": [],
        "style_guide": "",
        "category": "",
        "bbc_article_draft": "",
        "taylor_swift_tweet_draft": "",
        "feedback_history": [],
        "revision_count": 0,
        "final_approval": False
    }

    # Persistent variables to store the final results
    final_content = ""
    final_style_guide = ""

    print(f"Starting Workflow for Persona: {selected_persona.upper()}...")
    print("-" * 60)

    for output in app.stream(inputs):
        for node_name, state_update in output.items():
            print(f"\n[NODE COMPLETED: {node_name.upper()}]")

            if "retrieved_samples" in state_update:
                print(f"Found {len(state_update['retrieved_samples'])} reference samples.")

            if "style_guide" in state_update:
                final_style_guide = state_update["style_guide"]
                print("\n--- STYLE DNA EXTRACTED ---")
                print(final_style_guide)
                print("-" * 30)

            # Capture the drafts
            if "taylor_swift_tweet_draft" in state_update:
                final_content = state_update["taylor_swift_tweet_draft"]
                print(f"\n--- NEW TAYLOR SWIFT DRAFT ---\n{final_content}")

            if "bbc_article_draft" in state_update:
                final_content = state_update["bbc_article_draft"]
                print(f"\n--- NEW BBC DRAFT ---\n{final_content}")

            if "feedback_history" in state_update and state_update["feedback_history"]:
                print(f"\nCRITIC FEEDBACK:\n{state_update['feedback_history'][-1]}")

            if "revision_count" in state_update:
                print(f"Revision count: {state_update['revision_count']}")

            if "final_approval" in state_update:
                print(f"Final approval: {state_update['final_approval']}")

            print("\n" + "=" * 60 + "\n")

    # Return the final result so you can use it in other notebook cells
    return {
        "content": final_content,
        "style_guide": final_style_guide
    }


if __name__ == "__main__":
    mimic_model(topic="my new album is going to be INSANE", selected_persona="taylor_swift")