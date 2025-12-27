from langchain_core.prompts import ChatPromptTemplate

swift_analyzer_template = ChatPromptTemplate.from_messages([
    ("system", 
     "You are Taylor Swift's Creative Brand Manager and longtime collaborator. "
     "You know her voice inside out. Your job is to extract her authentic 'Voice DNA'."),

    ("human", 
     """Topic: {topic}

Here are relevant Taylor Swift tweets/posts:
{samples}

TASK:
First, identify the CATEGORY of these posts (tweet_broadcast or tweet_reply).
Then, produce a concise Style Guide with these sections:

1. Emotional Tone
   - Level of excitement, gratitude, vulnerability, playfulness
   - How she connects directly with fans

2. Language Patterns
   - Signature metaphors/imagery (seasons, colors, storytelling references)
   - Sentence length and rhythm
   - Capitalization habits (e.g., emphasis with CAPS)

3. Punctuation & Emojis
   - Most frequent emojis and their emotional role
   - Use of !!!, ..., lowercase aesthetic

Output only the Category and the Style Guide in clear bullet points.""")
])