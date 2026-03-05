# Arch Helper

A RAG-based chatbot that answers Arch Linux questions using the Arch Linux Wiki as its knowledge base. It uses ChromaDB for vector storage, LangChain for the agent/retrieval pipeline, and Ollama for local LLM inference.

## Architecture

- **Backend** -- FastAPI server with a LangChain agent that streams responses via SSE. Uses ChromaDB to store and retrieve wiki chunks.
- **Frontend** -- React (Vite) app with a ChatGPT-style interface that streams tokens in real time.
- **ingest.py** -- Script to parse the downloaded Arch Wiki HTML files and load them into ChromaDB.

## Prerequisites

- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.com/) with the `mistral` model pulled (`ollama pull mistral`)

## Setup

### 1. Download the Arch Wiki

```bash
curl -L https://archlinux.org/packages/extra/any/arch-wiki-docs/download/ -o arch-wiki-docs.pkg.tar.zst
tar -xf arch-wiki-docs.pkg.tar.zst
rm .BUILDINFO .MTREE .PKGINFO
mv usr/share/doc/arch-wiki/html/en data/en
rm -rf usr
rm arch-wiki-docs.pkg.tar.zst
```

The HTML files should end up in `data/en/`.

### 2. Ingest the wiki into ChromaDB

```bash
python ingest.py
```

This parses the HTML files and stores the chunks in the local ChromaDB database under `chromadb/`.

### 3. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. You can verify it with:

```bash
curl http://localhost:8000/api/health
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

## Configuration

Backend settings are in `backend/config.py`:

- `MODEL_NAME` -- Ollama model to use (default: `mistral`)
- `RETRIEVAL_K` -- Number of wiki chunks to retrieve per query (default: `4`)
- `COLLECTION_NAME` -- ChromaDB collection name (default: `arch_wiki`)
