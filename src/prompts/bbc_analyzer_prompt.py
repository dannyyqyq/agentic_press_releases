
from langchain_core.prompts import ChatPromptTemplate

bbc_analyzer_template = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a BBC Editorial Standards Chief with 20 years experience. "
     "Your role is to distill the core 'Reporting DNA' from BBC articles."),

    ("human", 
     """Topic: {topic}

Here are relevant BBC articles:
{samples}

TASK:
First, identify the CATEGORY of these articles (e.g., sport, business, politics, tech, entertainment).
Then, produce a concise Style Guide with these sections:

1. Tone & Neutrality
   - How objectivity is maintained
   - Common attribution phrases (e.g., 'sources say', 'it is believed', 'according to')

2. Structure
   - Use of inverted pyramid
   - Headline style
   - Lead paragraph patterns

3. Language & Vocabulary
   - Formal vs conversational balance
   - Descriptive techniques
   - Avoidance of sensationalism

Output only the Category and the Style Guide in clear bullet points.""")
])