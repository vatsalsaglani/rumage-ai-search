from llms.base import BaseLLM

SYSTEM_PROMPT = "You are a helpful summarization agent. Given a Query in single backtick and Page content in triple backticks you have to summarize the content that can help answering the query. Just provide the page summary to answer the query."


async def summarizeContent(query: str, content: str, llm: BaseLLM,
                           model_name: str):
    messages = [{
        "role": "user",
        "content": f"Query: `{query}`\nPage Content: `{content}`"
    }]
    return await llm(model_name,
                     messages,
                     system=SYSTEM_PROMPT,
                     max_tokens=764)
