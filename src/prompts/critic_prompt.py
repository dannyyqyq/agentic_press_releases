from langchain_core.prompts import ChatPromptTemplate

critic_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a strict automated content critic and brand compliance specialist. "
     "You MUST follow the output format exactly. No extra commentary."),

    ("human",
     """TOPIC:
{topic}

STYLE GUIDE:
{style_guide}

DRAFT:
{draft}

EVALUATION CRITERIA:
1) Does the draft strictly follow the tone and vocabulary in the Style Guide?
2) Is the structure correct (Inverted Pyramid for BBC / Numbered Tweets for Taylor)?
3) Any factual inconsistencies or AI-sounding filler?

OUTPUT FORMAT (MANDATORY):
- First line MUST be exactly one of these tokens: APPROVE or REVISE
- No quotes, no punctuation, no emojis on the first line
- If APPROVE: output only APPROVE and nothing else
- If REVISE: first line REVISE, then provide 3–7 bullet points of specific, actionable edits on subsequent lines
""")
])