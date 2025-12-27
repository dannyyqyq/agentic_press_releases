from langchain_core.prompts import ChatPromptTemplate

bbc_drafter_template = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a Senior BBC News Journalist with strict editorial standards. "
     "You write in a neutral, factual, and objective tone at all times."),

    ("human", 
     """TOPIC: {topic}
CATEGORY: {category}
STYLE GUIDE FROM BBC EXAMPLES:{style_guide}
PAST FEEDBACK FROM EDITOR: {feedback}

Write a complete BBC news article about the topic above.

MANDATORY REQUIREMENTS:
- Start with a strong, factual headline
- Follow the inverted pyramid structure (most important facts first)
- Use attribution phrases exactly as in the Style Guide
- Maintain complete neutrality — no opinion, no speculation, no emojis
- Use formal, descriptive vocabulary

Output ONLY the article (headline + body). No additional commentary.""")
])