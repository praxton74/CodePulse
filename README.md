# RepoMind 🧠

Chat with any GitHub repository in natural language. RepoMind ingests a codebase, understands it at the function/class level, and lets you ask questions, debug errors, and explore the repo's structure through an AI agent.

## What it does

Paste a GitHub URL, and RepoMind:
1. Clones the repo and parses every Python file using tree-sitter (AST-based chunking, not naive character splitting)
2. Embeds each function/class into ChromaDB with file path and line number metadata
3. Lets you chat with the codebase — an agent autonomously decides whether to search the code, search the web, or query GitHub's API to answer your question
4. Returns answers with precise citations (`file.py :: function_name :: line 12-18`)

## Demo
Example query: *"How does similarity search work in this repo?"*

> In `rag.py :: retrieve` (line 43-55), similarity search works by encoding the query into a vector, normalizing it, and searching a FAISS index for the top-k most similar vectors above a similarity threshold...

## Architecture
GitHub URL

│

▼

Clone repo (temp directory)

│

▼

tree-sitter parser ──► extract functions/classes with line numbers

│

▼

ChromaDB (embeddings + metadata)

│

▼

LangGraph Agent ──► decides which tool to use:

├── code_search   (RAG over the indexed codebase)

├── github_api    (PRs, issues, commits via PyGithub)

└── web_search     (Tavily, for external docs/errors)

│

▼

Answer with file:line citations

## Tech Stack

- **Agent & Orchestration:** LangGraph, LangChain
- **LLM:** Google Gemini 2.0 Flash (via `langchain-google-genai`)
- **Code Parsing:** tree-sitter (AST-based chunking at function/class level)
- **Vector Store:** ChromaDB with sentence-transformers embeddings (`all-MiniLM-L6-v2`)
- **GitHub Integration:** PyGithub
- **Web Search:** Tavily
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Observability:** LangSmith tracing

## Why tree-sitter instead of character-based chunking?

Most RAG systems split code into fixed-size character chunks, which often cuts functions in half and loses structural context. RepoMind parses the actual AST, so every chunk is a complete, named function or class — with exact line numbers preserved for accurate citations.

## Setup

### 1. Clone and install

```bash
git clone https://github.com/NotKshitiz/RepoMind.git
cd RepoMind
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file:
GEMINI_API_KEY=your_gemini_key

TAVILY_API_KEY=your_tavily_key

GITHUB_TOKEN=your_github_token

LANGCHAIN_TRACING_V2=true

LANGCHAIN_API_KEY=your_langsmith_key

LANGCHAIN_PROJECT=RepoMind

### 3. Run the backend

```bash
uvicorn api.routes:app --reload
```

### 4. Run the frontend

```bash
streamlit run frontend/app.py
```

Open `http://localhost:8501`, paste a GitHub URL, and start chatting.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|--------------|
| `/ingest` | POST | Clone, parse, and index a GitHub repo |
| `/chat` | POST | Ask a question about an indexed repo |

## Known Limitations

- Currently supports Python files only (JavaScript/TypeScript support planned)
- Single-GPU/local deployment, no distributed indexing
- GitHub API tool requires a personal access token with `public_repo` scope

## What's Next

- Multi-language support via tree-sitter grammars (JS, TS, Java, Go)
- Self-correction loop — agent re-queries when retrieval confidence is low
- Docker + docker-compose for one-command deployment

## Author

Kshitiz Kumar — [GitHub](https://github.com/NotKshitiz) |