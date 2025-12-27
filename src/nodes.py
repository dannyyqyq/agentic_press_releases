import logging
from langchain_openai import ChatOpenAI
from src.state import AgenticPRState
from openai import OpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langgraph.graph import StateGraph, END

from src.prompts import (
    bbc_analyzer_prompt, bbc_drafter_prompt, 
    critic_prompt, taylor_swift_analyzer_prompt, 
    taylor_swift_drafter_prompt
)
from pathlib import Path

# # Get the project root (assuming src/ is inside project)
# project_root = Path(__file__).parent.parent.resolve()  # Goes up from src/ to project root

logger = logging.getLogger("AgentNodes")
client = OpenAI()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# model config
model_name = "gpt-5-mini"
llm_strict = ChatOpenAI(model=model_name, temperature=0)
llm_creative_mid = ChatOpenAI(model=model_name, temperature=0.4) # For BBC
llm_creative_high = ChatOpenAI(model=model_name, temperature=0.8) # For Taylor


def load_vector_db():
    db_path = "chroma_db_test_run_0"
    embeddings = OpenAIEmbeddings()
    vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings,collection_name="taylor_bbc_dataset")

    doc_count = vector_db._collection.count()
    logger.info(f"Vectorstore loaded successfully! Collection: taylor_bbc_dataset")
    logger.info(f"Total documents: {doc_count}")

    if doc_count == 0:
        raise ValueError("Vector DB is empty! Wrong collection_name or rebuild needed.")
    
    return vector_db

def retriever_node(state: AgenticPRState):
    
    vector_db = load_vector_db()
    
    print(f"--- NODE: RETRIEVER (Targeting: {state['selected_persona']}) ---")
    topic = state["topic"]
    persona = state["selected_persona"]
    new_samples = []

    # Logic for BBC
    if persona  == "bbc":
        # Use your verified Tech/Politics/Ent filters
        bbc_docs = vector_db.similarity_search(topic, k=5, filter={"source": "bbc"})
        new_samples.extend([f"BBC REFERENCE: {d.page_content}" for d in bbc_docs])

    # Logic for Taylor Swift
    if persona == "taylor_swift":
        # Use your verified Broadcast/Reply filters
        swift_docs = vector_db.similarity_search(topic, k=5, filter={"source": "taylor_swift"})
        new_samples.extend([f"SWIFT REFERENCE: {d.page_content}" for d in swift_docs])

    # Return only the new data; operator.add handles the merge
    return {"retrieved_samples": new_samples}

def analyzer_node(state: AgenticPRState):
    print(f"--- NODE: ANALYZER (Categorizing: {state['selected_persona']}) ---")
    
    topic = state["topic"]
    persona = state["selected_persona"]
    samples_str = "\n\n".join(state["retrieved_samples"])

    # Execute chain
    if persona == "bbc":
        chain = bbc_analyzer_prompt.bbc_analyzer_template | llm_strict
    else:
        chain = taylor_swift_analyzer_prompt.swift_analyzer_template | llm_strict

    response = chain.invoke({"topic": topic, "samples": samples_str})
    raw_content = response.content

    # SPLITTING LOGIC
    try:
        # Extract category from the first part
        cat = parts[0].replace("CATEGORY:", "").strip()
        # Split by the marker we added to your template
        parts = raw_content.split("STYLE_DNA:")
        # Extract guide from the second part
        guide = parts[1].strip()
    except:
        cat = "General"
        guide = raw_content

    return {
        "style_guide": guide,
        "category": cat
    }
    
def drafter_node(state: AgenticPRState):
    print(f"--- NODE: DRAFTER (Targeting: {state['selected_persona']}) ---")
    
    topic = state["topic"]
    persona = state["selected_persona"]
    guide = state["style_guide"]
    category = state.get("category", "General") # Extracted by Analyzer
    
    feedback_list = state.get("feedback_history", [])     # If the list is empty, we send a 'None' message to the LLM
    latest_feedback = feedback_list[-1] if feedback_list else "No feedback yet. This is your first attempt."     # NEW: Get the latest feedback from the history

    # Select the chain
    if persona == "bbc":
        chain = bbc_drafter_prompt.bbc_drafter_template | llm_creative_mid
        response = chain.invoke({
            "topic": topic, 
            "style_guide": guide,
            "category": category,
            "feedback": latest_feedback # <--- PASSING FEEDBACK
        })
        return {"bbc_article_draft": response.content, "revision_count": state.get("revision_count", 0) + 1}
    
    if persona == "taylor_swift":
        chain = taylor_swift_drafter_prompt.taylor_drafter_template | llm_creative_high
        response = chain.invoke({
            "topic": topic, 
            "style_guide": guide, 
            "category": category,
            "feedback": latest_feedback # <--- PASSING FEEDBACK
        })
        
        return {
                    "taylor_swift_tweet_draft": response.content, 
                    "revision_count": state.get("revision_count", 0) + 1
                }
        
def critic_node(state: AgenticPRState):
    print(f"--- NODE: CRITIC (Checking: {state['selected_persona']}) ---")

    # Pick current draft
    current_draft = (
        state.get("bbc_article_draft", "")
        if state["selected_persona"] == "bbc"
        else state.get("taylor_swift_tweet_draft", "")
    )

    chain = critic_prompt.critic_prompt | llm_strict
    critic_response = chain.invoke({
        "topic": state["topic"],
        "style_guide": state["style_guide"],
        "draft": current_draft
    })

    content = (critic_response.content or "").strip()

    # Fail closed if empty output
    if not content:
        return {
            "final_approval": False,
            "feedback_history": ["Critic returned empty output. Please revise and resubmit."]
        }

    first_line = content.splitlines()[0].strip()

    # Normalize verdict:
    # - remove wrapping quotes/backticks
    # - remove trailing punctuation
    # - uppercase
    verdict = first_line.strip('\'"`').rstrip(".!:").upper()

    if verdict == "APPROVE":
        return {"final_approval": True}

    # If the critic didn't follow the protocol, treat everything as feedback
    # e.g. "Make these adjustments and resubmit."
    if not verdict.startswith("REVISE"):
        return {
            "final_approval": False,
            "feedback_history": [content]  # keep full text so drafter can use it
        }

    # Handle "REVISE: ..." same-line feedback + subsequent lines
    same_line_feedback = first_line
    same_line_feedback = same_line_feedback.strip('\'"`')
    # remove REVISE prefix from the first line
    same_line_feedback = same_line_feedback.upper().replace("REVISE", "", 1)
    same_line_feedback = same_line_feedback.lstrip(" :.-").strip()

    rest = "\n".join(content.splitlines()[1:]).strip()

    feedback = (same_line_feedback + ("\n" + rest if rest else "")).strip()
    if not feedback:
        feedback = "Revise to better match the style guide (critic did not provide specific edits)."

    return {
        "final_approval": False,
        "feedback_history": [feedback],
    }
    
# Router if continue or end the draft
def should_continue(state: AgenticPRState):
    # This function looks at the STATE, not the return value of a node
    if state["final_approval"] == True or state["revision_count"] >= 3:
        return "end"
    else:
        return "continue"
    
# 1. Initialize the Graph with our State schema
workflow = StateGraph(AgenticPRState)

# 2. Add our Nodes (The workers we built)
workflow.add_node("retriever", retriever_node)
workflow.add_node("analyzer", analyzer_node)
workflow.add_node("drafter", drafter_node)
workflow.add_node("critic", critic_node)

# 3. Define the Edges (The fixed paths)
workflow.set_entry_point("retriever") # Start here
workflow.add_edge("retriever", "analyzer")
workflow.add_edge("analyzer", "drafter")
workflow.add_edge("drafter", "critic")

# 4. Define the Conditional Edge (The feedback loop)
workflow.add_conditional_edges(
    "critic",
    should_continue,
    {
        "continue": "drafter", # Go back to Drafter for revisions
        "end": END             # Finish the process
    }
)

# 5. Compile the Graph
app = workflow.compile()