from abc import ABC, abstractmethod
from typing import List, Dict, Union, Literal
from pydantic import BaseModel, Field
from llms.base import BaseLLM
from llms.anthropic import AnthropicLLM
from llms.groq import GroqLLM
from claudetools.tools.tool import AsyncTool


class Query(BaseModel):
    query_idx: int = Field(..., description="Sequential index of the query")
    query_text: str = Field(
        ..., description="Text to query on Google or any other search engine")
    query_importance: Literal["High", "Medium", "Low"] = Field(
        ..., description="Importance of the query text.")
    query_aligned: bool = Field(
        ...,
        description="Will the query help in answering the main user query?")


class Queries(BaseModel):
    dependencies: List[Query] = Field(
        ...,
        description="List of all dependent queries.",
        min_length=4,
        max_length=5)


SYSTEM_PROMPT = """You're a powerful search engine query planning agent. Given a user message provide all the question or context dependencies that would need to be addressed to provide a response to the user.
You've to break down questions into its dependent queries such that the answers of the dependent query can be used to inform the parent question.
You don't need to answer the questions, simply provide the correct sequence of questions to ask and relevant dependencies.
Call the function with appropriate data i.e. the dependencies.
"""


class AnthropicPlanner:

    def __init__(self, api_key: str) -> None:
        self.tool = AsyncTool(anthropic_api_key=api_key)

    async def __call__(self, query: str):
        plan = await self.tool("claude-3-sonnet-20240229",
                               [{
                                   "role": "user",
                                   "content": f"Query: {query}"
                               }],
                               tools=[{
                                   "name": "planQuery",
                                   "description":
                                   "Plan the query dependencies",
                                   "parameters": Queries.model_json_schema()
                               }],
                               tool_choice={"name": "planQuery"},
                               attach_system=SYSTEM_PROMPT,
                               max_tokens=2048)
        plan = plan[0]
        if "parameters" in plan:
            return plan.get("parameters")
        else:
            return plan


if __name__ == "__main__":
    import asyncio
    from configs import ANTHROPIC_API_KEY
    ap = AnthropicPlanner(ANTHROPIC_API_KEY)
    # output = asyncio.run(ap("lok sabha election india 2024"))
    output = asyncio.run(ap("new from Apple"))
    print(output)
