from typing import TypedDict, List, Annotated, Literal, Optional
import operator

class AgenticPRState(TypedDict):
    """
    Shared state passed between agent nodes in the agentic PR workflow.
    Each node reads from and returns partial updates to this state.
    """
    # 1. Inputs from the user
    topic: str               
    selected_persona : Literal["bbc", "taylor_swift"]
    
    # 2. RAG results
    retrieved_samples: Annotated[List[str], operator.add] # Raw content from BBC and Taylor Swift - Annotated (previous value is added + any future values/list)
    # IE STEP1: retrieve 3 bbc articles [doc1,2,3]
    # STEP 2: retrieve 3 swift tweets [doc1,2,3, taylor1,2,3]
    
    # 3. Analysis & Instructions
    category: Optional[str]   # This will hold "Finance/Tech" OR "tweet_broadcast/tweet_reply" 
    style_guide: Optional[str]    # The "DNA" extracted by the Analyzer Agent 
    
    # 4. Drafts built
    bbc_article_draft: Optional[str]  # The BBC news article
    taylor_swift_tweet_draft: Optional[str]   # The Taylor Swift tweet thread
    
    # 5. Quality Control
    feedback_history: Annotated[List[str], operator.add]    # Notes from the Critic Agent
    
    # 6. Control logic
    revision_count: int      # To prevent infinite loops (e.g., max 3)
    final_approval: bool     # True if the Critic is happy