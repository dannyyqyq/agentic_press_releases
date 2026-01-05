# Style Mimic Agent: BBC & Taylor Swift Voice Generator

**An agentic LangGraph system that generates authentic content in two iconic styles using real data and self-reflective critique.**

Live Demo: [Custom GPT - Voice Echo](https://chatgpt.com/g/g-6950c302f4188191ae1fd265a744048c-voice-echo-bbc-or-taylor-swift)  
Backend API: [Railway Deployment](https://agenticpressreleases-production.up.railway.app/docs)

## Overview

This project implements a multi-agent workflow that mimics:
- **BBC News journalism**: Neutral, factual, structured, source-aware articles
- **Taylor Swift tweets**: Warm, poetic, vulnerable, emoji-rich threads with intimate lowercase voice

Built for an AI Solutions Engineer assessment — from prototype to deployed Custom GPT Action.

## Architecture
Retriever → Analyzer → Drafter → Critic → (Revision Loop) → Final Output

- **Retriever**: Semantic search over real BBC articles + Taylor Swift tweets (Chroma vector store)
- **Analyzer**: Extracts "Style DNA" — tone, structure, language patterns, emojis
- **Drafter**: Generates initial content conditioned on style guide
- **Critic**: Provides structured feedback; triggers revisions (up to 3 cycles)
- **State Management**: Typed `AgenticPRState` with accumulation for samples/feedback

## Key Features

- Real RAG grounding from Kaggle datasets
- Persona-specific prompt engineering (modular templates in `src/prompts/`)
- Self-improving loop via critic reflection
- Different LLM temperatures per agent role
- Deployed as production FastAPI backend on Railway
- Integrated as Custom GPT with Actions

## Tech Stack

- LangGraph + LangChain
- OpenAI (gpt series)
- Chroma vector store
- FastAPI + Uvicorn
- Railway (deployment)

## Local Setup

```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
uv run main.py  
```

## Project Challenges & Solutions
Here is a summary of the key challenges encountered during the development and deployment of the Style Mimic Agent, along with how they were overcome.

## Project Challenges & Solutions

Here is a summary of the key challenges encountered during the development and deployment of the Style Mimic Agent, along with how they were overcome.

| # | Challenge | Description | Solution | Key Lesson |
|---|-----------|-------------|----------|------------|
| 1 | **Vector Store Retrieval Returning 0 Results** | Retrieval worked in notebooks (5 samples) but returned 0 in scripts and deployment. | Caused by relative paths, Chroma UUID subfolders, missing `collection_name`, and cwd differences. Fixed with identifying the UUID folder, and specifying `collection_name="taylor_bbc_dataset"`. | Deployment environments differ from notebooks — use robust path resolution and explicitly verify metadata/collection names. |
| 2 | **Railway Deployment Crashes ("Application failed to respond")** | Local `uvicorn` worked perfectly, but Railway showed 502 errors on startup. | Issues: missing `__init__.py` in `src/`, incorrect start command, env vars. Fixed by adding `__init__.py`, using `uvicorn api:app --host 0.0.0.0 --port $PORT`, and setting `OPENAI_API_KEY`. | Local success ≠ deployment success. Align package structure, port binding, and environment variables precisely. |
| 3 | **Critic Strictness & Lack of Final Approval** | Critic (especially BBC mode) was very rigorous and rarely approved. | Intentional for quality — capped revisions at 3 and output the best draft regardless. | A strict critic drives higher authenticity; rigor is a feature when mimicking high-standard voices. |
| 4 | **Generation Latency (3–6 minutes)** | Multiple LLM calls across agents caused long wait times. | Accepted as trade-off for depth; clearly communicated in GPT instructions and pre-interview email. | High-fidelity agentic loops prioritize quality over speed — set user expectations transparently. |
| 5 | **Custom GPT Public Sharing Restriction** | Could not share GPT link publicly without privacy policy. | Created a simple privacy policy page via GitHub Pages and linked it in GPT settings. | External Actions require compliance (privacy policy) for public sharing — quick to resolve with a static page. |
| 6 | **GPT Action Flagged for Policy Violation** | After deployment, the Custom GPT was flagged during OpenAI's review process, preventing public sharing. | Likely due to perceived impersonation or misinformation risk from mimicking real entities (BBC/Taylor Swift). Resolved by adding strong disclaimers in instructions ("fictional content for creative purposes only, not affiliated"), renaming to emphasize "inspired by" style, and including a footer disclaimer in every response. | OpenAI is cautious about style mimicry of celebrities/brands and news generation — clear, upfront disclaimers and non-affiliation statements are essential for compliance. |

These challenges reinforced the importance of **defensive engineering, thorough debugging with logs, clear user communication, and platform-specific compliance** in production AI systems.

The result: a robust, deployed agentic workflow producing remarkably authentic BBC articles and Taylor Swift tweets.
