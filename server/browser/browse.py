import time
import json
import asyncio
import traceback
from playwright.async_api import async_playwright
from typing import Union

from agent.summarize import summarizeContent
from llms.anthropic import AnthropicLLM
from llms.groq import GroqLLM


async def evaluate_text(query: str, page, llm: Union[GroqLLM, AnthropicLLM],
                        model_name: str):
    text_content = await page.evaluate('''() => {
            const tags = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'p', 'span', 'a', 'strong', 'b', 'em', 'i',
                'mark', 'small', 'del', 'ins', 'sub', 'sup',
                'ul', 'ol', 'li', 'dl', 'dt', 'dd',
                'blockquote', 'q', 'cite', 'abbr', 'address',
                'pre', 'code', 'samp', 'kbd'
            ];
            let text = '';

            tags.forEach(tag => {
                const elements = document.querySelectorAll(tag);
                elements.forEach(element => {
                    if (tag === 'a') {
                        // Optionally handle links differently, e.g., include the href attribute
                        const href = element.getAttribute('href');
                        text += `[Link: ${href}] ${element.textContent.trim()}\n`;
                    } else {
                        text += `${element.textContent.trim()}\n`;
                    }
                });
            });

            return text;
        }''')
    # print(f"TEXT CONTENT: \n", len(text_content.split()))
    summary = await summarizeContent(query, text_content, llm, model_name)
    # print(f"Summary: \n{summary}")
    return summary


async def get_page_text_content(url: str, search_query: str,
                                llm: Union[GroqLLM, AnthropicLLM], model_name):
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            # print(f'Going to URL: {url}')
            await page.goto(url)
            # print(f'URL Opened\nWaiting for page load')
            await page.wait_for_load_state("load")
            # print(f'Page loaded\nGetting text content')
            # text_content = await page.evaluate('''() => {
            #             return document.body.textContent || ""
            #         }''')
            text_content = await evaluate_text(search_query, page, llm,
                                               model_name)
            # print(f'Got Text Content')
            await browser.close()
            return {"url": url, "textContent": text_content}
        except Exception as err:
            return {}


async def retrieve_search_links(search_query):
    try:
        async with async_playwright() as p:
            st_time = time.time()
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://www.google.com')
            await page.wait_for_selector("id=APjFqb", state='visible')
            await page.fill("id=APjFqb", search_query)
            await page.press('id=APjFqb', 'Enter')
            await page.wait_for_load_state('load')

            links = await page.evaluate('''() => {
                const anchors = Array.from(document.querySelectorAll('a'));
                return anchors
                    .map(anchor => anchor.href)
                    .filter(href => href.startsWith('https://') && !href.includes('.google.'));
            }''')
            en_time = time.time()
            # print(f'TIME TAKEN TO FETCH LINKS: {en_time - st_time}')
            # print("Filtered Links:", links)
            await browser.close()
            return links
    except Exception as err:
        print(f"EXCEPTION: {str(err)}")
        print(traceback.format_exc())
        return []


async def get_search_results(search_query,
                             llm: Union[GroqLLM, AnthropicLLM],
                             model_name,
                             min_searches: int = 1):
    links = await retrieve_search_links(search_query)
    top_results_urls = links[:min_searches]
    contents = await asyncio.gather(*[
        get_page_text_content(url, search_query, llm, model_name)
        for url in top_results_urls
    ],
                                    return_exceptions=True)
    # print(json.dumps(contents, indent=4))
    return contents
