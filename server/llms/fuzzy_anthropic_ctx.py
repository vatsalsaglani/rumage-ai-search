def manageContext(messages, max_words: int = 120_000):
    keep_messages = []
    total_len = 0
    for message in messages[::-1]:
        message_content = message.get("content")
        words = list(map(lambda m: m.strip(), message_content.split()))
        if len(words) > max_words:
            words = words[:max_words - 1]
            keep_messages += [{
                "role": message.get("role"),
                "content": " ".join(words)
            }]
            break
        else:
            current_len = total_len + len(words)
            if current_len >= max_words:
                words = words[current_len - max_words:]
                keep_messages += [{
                    "role": message.get("role"),
                    "content": " ".join(words)
                }]
                break
            else:
                total_len += len(words)
                keep_messages += [{
                    "role": message.get("role"),
                    "content": " ".join(words)
                }]
    # print(f"TOTAL LEN: {total_len}")
    return keep_messages[::-1], total_len
