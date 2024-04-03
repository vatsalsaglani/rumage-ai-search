import tiktoken
from typing import List, Dict


class MessageManagement:
    """Removes tokens from start or end and provides string with max token lenght provided"""

    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        self.encoding = tiktoken.encoding_for_model(model_name)

    def __count_tokens__(self, content: str):
        tokens = self.encoding.encode(content)
        return len(tokens) + 4

    def __pad_message__(self, content: str, num_tokens: int):
        tokens = self.encoding.encode(content)
        return self.encoding.decode(tokens[:num_tokens])

    def __call__(self, messages: List[Dict], max_length: int = 14_000):
        system_prompt = list(
            filter(lambda message: message.get("role") == "system", messages))
        other_messages = list(
            filter(lambda message: message.get("role") != "system", messages))

        managed_messages = []
        managed_messages += system_prompt
        curr_length = 0
        if len(system_prompt) == 1:
            curr_length += self.__count_tokens__(
                system_prompt[0].get("content"))
        for message in other_messages[::-1]:
            if message.get("role") == "system":
                managed_messages += message
            else:
                lgth = self.__count_tokens__(message.get("content"))
                if curr_length + lgth >= max_length:
                    tokens_to_keep = max_length - curr_length
                    # print(f"TOKENS TO KEEP: ", tokens_to_keep)
                    if tokens_to_keep > 0:
                        padded_message = self.__pad_message__(
                            message.get("content"), tokens_to_keep)
                        message["content"] = padded_message
                        managed_messages.append(message)
                        curr_length += tokens_to_keep
                        break
                    else:
                        break
                else:
                    managed_messages.append(message)
                    curr_length += lgth
        return managed_messages
