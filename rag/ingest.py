#!/usr/bin/env python3
"""Ingest GraphXR Help Center AsciiDoc files into a ChromaDB vector store."""

import sys
import time
from pathlib import Path

import chromadb
from openai import OpenAI
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn

from config import (
    LM_STUDIO_BASE_URL,
    LM_STUDIO_API_KEY,
    EMBEDDING_MODEL,
    DOCS_DIR,
    CHROMA_DIR,
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

console = Console()


def load_documents(docs_dir: Path) -> list[dict]:
    """Recursively load all .adoc files and return list of {path, content}."""
    documents = []
    for adoc_path in sorted(docs_dir.rglob("*.adoc")):
        try:
            content = adoc_path.read_text(encoding="utf-8")
            if content.strip():
                documents.append({
                    "path": str(adoc_path.relative_to(docs_dir)),
                    "content": content,
                })
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read {adoc_path}: {e}[/yellow]")
    return documents


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks by character count, breaking on paragraph boundaries."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_text + "\n\n" + para
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def get_embeddings(client: OpenAI, texts: list[str], model: str) -> list[list[float]]:
    """Get embeddings for a batch of texts. Batches in groups of 32 to avoid overloading."""
    all_embeddings = []
    batch_size = 32
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        cleaned = [t.replace("\n", " ") for t in batch]
        response = client.embeddings.create(input=cleaned, model=model)
        all_embeddings.extend([d.embedding for d in response.data])
    return all_embeddings


def main():
    console.print("[bold blue]GraphXR Help Center — Document Ingestion[/bold blue]\n")

    if not DOCS_DIR.exists():
        console.print(f"[red]Error: Documents directory not found: {DOCS_DIR}[/red]")
        sys.exit(1)

    # Load documents
    with console.status("Loading AsciiDoc files..."):
        documents = load_documents(DOCS_DIR)
    console.print(f"Loaded [green]{len(documents)}[/green] documents")

    # Chunk documents
    with console.status("Chunking documents..."):
        chunks = []
        for doc in documents:
            doc_chunks = chunk_text(doc["content"], CHUNK_SIZE, CHUNK_OVERLAP)
            for i, chunk in enumerate(doc_chunks):
                chunks.append({
                    "id": f"{doc['path']}::chunk_{i}",
                    "text": chunk,
                    "metadata": {"source": doc["path"], "chunk_index": i},
                })
    console.print(f"Created [green]{len(chunks)}[/green] chunks")

    # Initialize ChromaDB
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    existing = [c.name for c in chroma_client.list_collections()]
    if COLLECTION_NAME in existing:
        chroma_client.delete_collection(COLLECTION_NAME)
        console.print(f"Deleted existing collection [yellow]{COLLECTION_NAME}[/yellow]")

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Embed and store
    client = OpenAI(base_url=LM_STUDIO_BASE_URL, api_key=LM_STUDIO_API_KEY)

    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    console.print(f"\nEmbedding chunks with [cyan]{EMBEDDING_MODEL}[/cyan]...")
    start = time.time()

    batch_size = 32
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Embedding...", total=len(texts))
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            batch_ids = ids[i : i + batch_size]
            batch_meta = metadatas[i : i + batch_size]

            embeddings = get_embeddings(client, batch_texts, EMBEDDING_MODEL)
            collection.add(
                ids=batch_ids,
                embeddings=embeddings,
                documents=batch_texts,
                metadatas=batch_meta,
            )
            progress.advance(task, len(batch_texts))

    elapsed = time.time() - start
    console.print(f"\n[bold green]Done![/bold green] Ingested {len(chunks)} chunks in {elapsed:.1f}s")
    console.print(f"Vector store saved to [cyan]{CHROMA_DIR}[/cyan]")


if __name__ == "__main__":
    main()
