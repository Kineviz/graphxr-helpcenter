# GraphXR Help Center RAG

A retrieval-augmented generation pipeline for the GraphXR documentation, powered by LM Studio.

## Prerequisites

- [LM Studio](https://lmstudio.ai/) running locally with the server enabled on port 1234
- Load these models in LM Studio:
  - **Inference:** `qwen/qwen3.5-9b`
  - **Embedding:** `text-embedding-mxbai-embed-large-v1`

## Setup

```bash
cd rag
uv sync
```

## Usage

### 1. Ingest documents

Loads the AsciiDoc files, chunks them, generates embeddings, and stores them in a local ChromaDB vector store.

```bash
uv run python ingest.py
```

### 2. Query

**Interactive mode** (REPL):

```bash
uv run python query.py
```

**Single question:**

```bash
uv run python query.py "How do I import CSV files into GraphXR?"
```

**Options:**

| Flag | Description |
|------|-------------|
| `--top-k N` | Number of document chunks to retrieve (default: 5) |
| `--no-sources` | Hide source document references in output |

## Configuration

Edit `config.py` to change models, chunk sizes, or the LM Studio URL.
