from openai import AsyncOpenAI
import random
import asyncio
import traceback
from typing import List, Dict, Union
from llms.base import BaseLLM
from llms.openai_ctx import MessageManagement
from openai import RateLimitError
import backoff


class OpenAILLM(BaseLLM):

    def __init__(self, api_key: str | None = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key)

    @backoff.on_exception(backoff.expo, RateLimitError, max_tries=3)
    async def __call__(self, model: str, messages: List[Dict], **kwargs):
        try:
            if "system" in kwargs:
                messages = [{
                    "role": "system",
                    "content": kwargs.get("system")
                }] + messages
                del kwargs["system"]
            manageContext = MessageManagement()
            messages = manageContext(messages,
                                     kwargs.get("ctx_length", 100_000))
            # print(f"OPENAI MESSAGES: ", messages)
            print(model)
            await asyncio.sleep(random.choice([0.5, 1, 0.8, 0.9]))
            output = await self.client.chat.completions.create(
                messages=messages, model=model, temperature=0.2, **kwargs)
            output_content = output.choices[0].message.content
            # print("OUTPUT Content: ", output_content)
            return output_content
        except RateLimitError:
            raise RateLimitError
        except Exception as err:
            print(f"ERROR: {str(err)}")
            print(f"{traceback.format_exc()}")
            return ""


class OpenAILLMStream(BaseLLM):

    def __init__(self, api_key: str | None = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key)

    async def __call__(self, model: str, messages: List[Dict], **kwargs):
        if "system" in kwargs:
            messages = [{
                "role": "system",
                "content": kwargs.get("system")
            }] + messages
            del kwargs["system"]
        manageContext = MessageManagement()
        messages = manageContext(messages, kwargs.get("ctx_length", 100_000))
        print(model)
        await asyncio.sleep(random.choice([0.5, 1, 0.8, 0.9]))
        stream = await self.client.chat.completions.create(model=model,
                                                           messages=messages,
                                                           temperature=0.2,
                                                           stream=True,
                                                           **kwargs)
        async for chunk in stream:
            yield chunk.choices[0].delta.content or ""
