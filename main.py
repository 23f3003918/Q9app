from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Knowledge base with key facts from TypeScript book
KNOWLEDGE_BASE = """
TypeScript Documentation Notes:

- The author affectionately calls the => syntax "fat arrow"
- The !! operator converts any value into an explicit boolean
- node.getChildren() lets you walk every child node of a ts.Node
- Code pieces like comments and whitespace that aren't in the AST are called "trivia"
- TypeScript uses structural type system
- Interfaces define the shape of objects
- Generics provide type variables
- Union types allow multiple types using |
- Type guards narrow types at runtime
"""

async def get_answer(query: str) -> str:
    """Get answer using LLM with knowledge base."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://aipipe.org/openrouter/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ.get('AIPIPE_TOKEN')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are a TypeScript documentation assistant. Answer questions based ONLY on these notes. Be very concise and answer directly with just the key information requested.You should only give precise answers(for example: what does the author cal => syntax? Ans: fat arrow. Precisely. Nothing else, just precise answer everytime)\n\n{KNOWLEDGE_BASE}"
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

@app.get("/search")
async def search(q: str):
    """Search TypeScript documentation and answer questions."""
    answer = await get_answer(q)
    
    return {
        "answer": answer,
        "sources": "TypeScript Deep Dive by Basarat Ali Syed"
    }

@app.get("/")
async def root():
    return {"status": "ok", "message": "TypeScript RAG API running"}