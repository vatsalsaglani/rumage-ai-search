import asyncio
import time
from browser.browse import (get_search_results, retrieve_search_links,
                            get_page_text_content)
from llms.anthropic import AnthropicLLM, AnthropicLLMStream
from llms.groq import GroqLLM, GroqLLMStream
from llms.openai_complete import OpenAILLM, OpenAILLMStream
from agent.query_planning import AnthropicPlanner
from configs import (ANTHROPIC_API_KEY, GROQ_API_KEY, ANTHROPIC_ANSWER_MODEL,
                     ANTHROPIC_CONTENT_SUMMARY_MODEL, GROQ_ANSWER_MODEL,
                     GROQ_CONTENT_SUMMARY_MODEL, OPENAI_API_KEY, OPENAI_MODEL,
                     QUERY_PLANNING_LLM_NAME, WEB_PAGE_SUMMARY_LLM_NAME,
                     ANSWERING_LLM_NAME)

llm = AnthropicLLM(ANTHROPIC_API_KEY)
llm_stream = AnthropicLLMStream(ANTHROPIC_API_KEY)

groq_llm = GroqLLM(GROQ_API_KEY)
groq_llm_stream = GroqLLMStream(GROQ_API_KEY)

openai_llm = OpenAILLM(OPENAI_API_KEY)

SEARCH_PROMPT = """Given a search query in <query></query> and the search results in <search-results></search-results> try to answer the search query as precisely as possible. Try to provide citation links for the URL of result. Only answer if the answer is possible from the search results, else politely reply that you didn't find anything relevant.
Provide as much explanation as you can but don't go to overboard.
Note: Always provide inline markdown citations for the links in the answer. The link should always be in markdown. For example, if the link is https://google.com then you show [Google](https://google.com). Link is nothing but the `url` from which the content is retrieved.
"""

llm2class = {
    "anthropic": {
        "completion": AnthropicLLM,
        "stream": AnthropicLLMStream,
        "api_key": ANTHROPIC_API_KEY,
        "content_summary_model": ANTHROPIC_CONTENT_SUMMARY_MODEL,
        "answering_model": ANTHROPIC_ANSWER_MODEL
    },
    "groq": {
        "completion": GroqLLM,
        "stream": GroqLLMStream,
        "api_key": GROQ_API_KEY,
        "content_summary_model": GROQ_CONTENT_SUMMARY_MODEL,
        "answering_model": GROQ_ANSWER_MODEL
    },
    "openai": {
        "completion": OpenAILLM,
        "stream": OpenAILLMStream,
        "api_key": OPENAI_API_KEY,
        "content_summary_model": OPENAI_MODEL,
        "answering_model": OPENAI_MODEL
    }
}


async def search(search_query: str, llm_name: str):
    # print(f'**Getting Search Results**')
    llm = llm2class[llm_name]["completion"](llm2class[llm_name]["api_key"])
    llm_stream = llm2class[llm_name]["stream"](llm2class[llm_name]["api_key"])
    results = await get_search_results(
        search_query,
        llm,
        llm2class[llm_name]["content_summary_model"],
        min_searches=3)
    # print(f'**Search Results Available**')
    messages = [{
        "role":
        "user",
        "content":
        f"<query>{search_query}</query>\n<search-result>{results}</search-results>"
    }]
    # print(f'**Answer:\n**')
    async for text in llm_stream(llm2class[llm_name]["answering_model"],
                                 messages,
                                 system=SEARCH_PROMPT,
                                 max_tokens=2048):
        yield text


flatten = lambda lst: [item for sublist in lst for item in sublist]


async def plannedSearch(search_query: str, min_links_per_query: int = 3):

    planner = AnthropicPlanner(ANTHROPIC_API_KEY)
    web_page_summary_llm = llm2class[WEB_PAGE_SUMMARY_LLM_NAME]["completion"](
        llm2class[WEB_PAGE_SUMMARY_LLM_NAME].get("api_key"))
    answering_llm = llm2class[ANSWERING_LLM_NAME]["stream"](
        llm2class[ANSWERING_LLM_NAME].get("api_key"))
    # extract dependencies
    yield "_Planning Queries_\n"
    dependencies = await planner(search_query)
    dependencies = dependencies.get("dependencies")
    dep_yeild_text = """"""
    for dep in dependencies:
        dep_yeild_text += f"- {dep.get('query_text')}\n"
    yield dep_yeild_text
    yield "  \n"
    # print(f"Planned Queries: {dependencies}")
    yield "\n- Searching for individual Queries"
    queries = [d.get("query_text") for d in dependencies] + [search_query]
    st_time = time.time()
    links = await asyncio.gather(*[retrieve_search_links(d) for d in queries],
                                 return_exceptions=True)
    en_time = time.time()
    links = flatten([l[:min_links_per_query] for l in links])
    links = list(set(links))
    search_time = en_time - st_time
    yield f"\n- Search Completed _({search_time:.3f}s)_"
    yield f"\n- Summarizing __*{len(links)}*__ links"
    # print(f'Final Set of Links: {links}')
    # NOTE: Use the concurrent one when no rate limit issues
    st_time = time.time()
    retrieved_summarized_contents = await asyncio.gather(*[
        get_page_text_content(
            url, search_query, web_page_summary_llm,
            llm2class[WEB_PAGE_SUMMARY_LLM_NAME].get("content_summary_model"))
        for url in links
    ],
                                                         return_exceptions=True
                                                         )
    en_time = time.time()
    summarization_time = en_time - st_time
    yield f"\n- Summarization Completed _({summarization_time:.3f}s)_"
    # NOTE: When rate limited use this sequential
    # retrieved_summarized_contents = []
    # for _, url in enumerate(tqdm(links)):
    #     retrieved_summarized_contents.append(await get_page_text_content(
    #         url, search_query, llm,
    #         llm2class[llm_name].get("content_summary_model")))
    #     await asyncio.sleep(0.5)
    # print(f"retrieved_summarized_contents: {retrieved_summarized_contents}")
    # print(f'**Search Results Available**')
    yield f"\n### Search Result\n\n\n\n"
    messages = [{
        "role":
        "user",
        "content":
        f"<query>{search_query}</query>\n<search-result>{retrieved_summarized_contents}</search-results>"
    }]
    async for text in answering_llm(
            llm2class[ANSWERING_LLM_NAME]["answering_model"],
            messages,
            system=SEARCH_PROMPT,
            max_tokens=3000):
        yield text


if __name__ == "__main__":
    import asyncio
    while True:
        search_query = str(input(f"\nPlease input your search: \n"))
        if len(search_query.strip()) > 0:
            asyncio.run(search(search_query))
        else:
            pass
