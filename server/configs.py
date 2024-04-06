import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

ANTHROPIC_ANSWER_MODEL = os.environ.get("ANTHROPIC_ANSWER_MODEL",
                                        "claude-3-sonnet-20240229")
ANTHROPIC_CONTENT_SUMMARY_MODEL = os.environ.get(
    "ANTHROPIC_CONTENT_SUMMARY_MODEL", "claude-3-haiku-20240307")

GROQ_ANSWER_MODEL = os.environ.get("GROQ_ANSWER_MODEL", "mixtral-8x7b-32768")
GROQ_CONTENT_SUMMARY_MODEL = os.environ.get("GROQ_CONTENT_SUMMARY_MODEL",
                                            "mixtral-8x7b-32768")
GROQ_CONTENT_SUMMARY_MODEL_FALLBACK_GEMMA = "gemma-7b-it"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

OPENAI_MODEL = os.environ.get("OPENAI_MODEL")

QUERY_PLANNING_LLM_NAME = os.environ.get("QUERY_PLANNING_LLM_NAME")
WEB_PAGE_SUMMARY_LLM_NAME = os.environ.get("WEB_PAGE_SUMMARY_LLM_NAME")
ANSWERING_LLM_NAME = os.environ.get("ANSWERING_LLM_NAME")

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
MISTRAL_ANSWER_MODEL = os.environ.get("MISTRAL_ANSWER_MODEL")
MISTRAL_CONTENT_SUMMARY_MODEL = os.environ.get("MISTRAL_CONTENT_SUMMARY_MODEL")
