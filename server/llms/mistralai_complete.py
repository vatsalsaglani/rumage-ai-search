from mistralai.async_client import MistralAsyncClient
from mistralai.models.chat_completion import ChatMessage
import random
import asyncio
from typing import List, Dict
from llms.base import BaseLLM
from llms.mistral_ctx import MistralAICtx
from mistralai.exceptions import MistralAPIStatusException
import backoff
import traceback


class MistralAILLM(BaseLLM):

    def __init__(self, api_key: str | None = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = MistralAsyncClient(api_key=api_key)

    @backoff.on_exception(backoff.expo, MistralAPIStatusException, max_tries=3)
    async def __call__(self, model: str, messages: List[Dict], **kwargs):
        try:
            if "system" in kwargs:
                messages[0]["content"] = kwargs.get(
                    "system") + "\n\n" + messages[0].get("content")
                del kwargs["system"]
            manageContext = MistralAICtx(model)
            messages = manageContext(messages,
                                     kwargs.get("ctx_length", 28_000))
            await asyncio.sleep(random.choice([0.5, 1, 0.8, 0.9]))
            _messages = [ChatMessage(**m) for m in messages]
            output = await self.client.chat(model=model,
                                            messages=_messages,
                                            temperature=0.2,
                                            **kwargs)
            print(output)
            return output.choices[0].message.content
        except MistralAPIStatusException:
            raise MistralAPIStatusException
        except Exception as err:
            print(f"ERROR: {str(err)}")
            print(f"{traceback.format_exc()}")
            return ""


class MistralAILLMStream(BaseLLM):

    def __init__(self, api_key: str | None = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = MistralAsyncClient(api_key=api_key)

    async def __call__(self, model: str, messages: List[Dict], **kwargs):
        if "system" in kwargs:
            messages[0]["content"] = kwargs.get(
                "system") + "\n\n" + messages[0].get("content")
            del kwargs["system"]
        manageContext = MistralAICtx(model)
        messages = manageContext(messages, kwargs.get("ctx_length", 28_000))
        await asyncio.sleep(random.choice([0.5, 1, 0.8, 0.9]))
        _messages = [ChatMessage(**m) for m in messages]
        response = self.client.chat_stream(model=model,
                                           messages=_messages,
                                           temperature=0.2,
                                           **kwargs)

        async for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
