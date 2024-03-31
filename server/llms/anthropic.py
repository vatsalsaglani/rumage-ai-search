import traceback
from anthropic import AsyncAnthropic, RateLimitError
from llms.fuzzy_anthropic_ctx import manageContext
from llms.base import BaseLLM
from typing import List, Dict, Union
import backoff


class AnthropicLLM(BaseLLM):

    def __init__(self, api_key: Union[str, None] = None):
        super().__init__(api_key)
        self.client = AsyncAnthropic(api_key=api_key)

    @backoff.on_exception(backoff.expo, RateLimitError, max_tries=3)
    async def __call__(self, model: str, messages: List[Dict], **kwargs):
        try:
            messages, _ = manageContext(messages)
            output = await self.client.messages.create(model=model,
                                                       messages=messages,
                                                       **kwargs)
            # print(f"OUTPUT: \n {output}")
            return output.content[0].text
        except RateLimitError:
            raise RateLimitError
        except Exception as err:

            print(f"ERROR: {str(err)}")
            print(f"{traceback.format_exc()}")
            return ""


class AnthropicLLMStream(BaseLLM):

    def __init__(self, api_key: Union[str, None] = None):
        super().__init__(api_key)
        self.client = AsyncAnthropic(api_key=api_key)

    async def __call__(self, model: str, messages: List[Dict], **kwargs):
        messages, _ = manageContext(messages)
        async with self.client.messages.stream(model=model,
                                               messages=messages,
                                               **kwargs) as stream:
            async for text in stream.text_stream:
                yield text
