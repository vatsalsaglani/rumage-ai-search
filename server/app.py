from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Union, Literal

from search import search, plannedSearch

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    return {"ok": True}


@app.get("/search")
async def search_api(q: str, llm: Literal["groq", "anthropic"]):
    return StreamingResponse(search(q, llm), media_type="text/event-stream")


@app.get("/plannedSearch")
async def plannedSearch_api(q: str):
    return StreamingResponse(plannedSearch(q))


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8899, reload=True)
