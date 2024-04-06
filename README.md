# Rumage (AI-Search)

A GenerativeAI Search wrapper around Google Search with query planning capabilities. Uses Playwright to automate search and extract search links.

## Demo

### Bookstore search 

https://github.com/vatsalsaglani/rumage-ai-search/assets/23306338/b172930c-ee21-451c-9a96-f72d94cd8f32

### Resolving SQL Error

https://github.com/vatsalsaglani/rumage-ai-search/assets/23306338/2836735d-3eab-4b8d-b5b6-80c4ac27286c

## Setup

### 1. Install Python Requirements

```sh
pip install -r server/requirements.txt
```

### 2. Install Playwright

```sh
playwright install chromium 
```

### 3. Install UI Dependencies

```sh
cd ui/
npm i
```

### 4. Create .env file and add your keys and configs

```
ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
GROQ_API_KEY="YOUR_GROQ_API_KEY"

ANTHROPIC_ANSWER_MODEL = "claude-3-haiku-20240307"
ANTHROPIC_CONTENT_SUMMARY_MODEL = "claude-3-haiku-20240307"

GROQ_ANSWER_MODEL="mixtral-8x7b-32768"
GROQ_CONTENT_SUMMARY_MODEL="mixtral-8x7b-32768"

OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
OPENAI_MODEL="gpt-4-turbo-preview"

MISTRAL_API_KEY="YOUR_MISTRALAI_API_KEY"
MISTRAL_ANSWER_MODEL="mistral-medium-latest"
MISTRAL_CONTENT_SUMMARY_MODEL="mistral-small-latest"

QUERY_PLANNING_LLM_NAME="anthropic"
WEB_PAGE_SUMMARY_LLM_NAME="mistralai"
ANSWERING_LLM_NAME="openai"
```
> You can update the model names here as per your liking. Remember if you update the models please update the max tokens in the respective context management in `server/llms/`

### 5. Start Server

```sh
cd server/
python app.py
```

### 6. Start UI

```sh
cd ui/
npm run dev
```