# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
cd RAGminProject && pip install -r requirements.txt

# Run FastAPI web server (SSE streaming)
python web_app.py
# or: uvicorn web_app:app --host 0.0.0.0 --port 8000

# Streamlit chat UI
streamlit run app_qa.py

# Streamlit file upload UI
streamlit run app_file_uploader.py
```

## Environment

- `DASHSCOPE_API_KEY` — required (阿里云 DashScope key)
- `RAG_DEBUG_PROMPTS=1` — prints full prompt templates to stdout

## Architecture

```
RAGminProject/
├── config_data.py          # Global config (model names, chunking, retriever k)
├── rag.py                  # Rag class: retriever → prompt → ChatTongyi → stream
├── vector_store.py         # Chroma wrapper, returns retriever
├── knowledge_base.py       # Text ingestion with MD5 dedup, writes to Chroma
├── file_history_store.py   # File-based session history (JSONL per session_id)
├── web_app.py              # FastAPI app with built-in HTML chat page (SSE)
├── app_qa.py               # Streamlit chat interface
└── app_file_uploader.py    # Streamlit TXT uploader → knowledge_base
```

Key flow: `Rag.__init__` builds a chain via `RunnableWithMessageHistory`:
`user_input → retriever (vector similarity) → context + history → ChatPromptTemplate → ChatTongyi → StrOutputParser`

Chat history is persisted per `session_id` in `chat_history/`. `config.session_config` defaults to `"user_001"`.

## Config notes

- `config_data.py` controls all tunables: `text_model`, `chat_model`, `chunk_size`, `chunk_overlap`, `similarity_top_k`, `persist_directory`
- Current models: `text-embedding-v4` (embedding), `qwen3-max` (chat)
