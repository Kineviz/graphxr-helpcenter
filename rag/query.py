#!/usr/bin/env python3
"""CLI for querying the GraphXR Help Center RAG pipeline."""

import argparse
import sys

import chromadb
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from config import (
    LM_STUDIO_BASE_URL,
    LM_STUDIO_API_KEY,
    INFERENCE_MODEL,
    EMBEDDING_MODEL,
    CHROMA_DIR,
    COLLECTION_NAME,
    TOP_K,
)

console = Console()

SYSTEM_PROMPT = """\
You are a helpful assistant for GraphXR, a graph visualization and analytics platform by Kineviz.
Answer questions using ONLY the provided context from the GraphXR documentation.
If the context doesn't contain enough information to answer, say so honestly.
Be concise and specific. Reference relevant features or UI elements by name when possible."""


def get_query_embedding(client: OpenAI, text: str, model: str) -> list[float]:
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def retrieve(collection, query_embedding: list[float], top_k: int) -> list[dict]:
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    docs = []
    for i in range(len(results["ids"][0])):
        docs.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i] if results.get("distances") else None,
        })
    return docs


def build_prompt(question: str, context_docs: list[dict]) -> str:
    context_parts = []
    for i, doc in enumerate(context_docs, 1):
        context_parts.append(f"[Source {i}: {doc['source']}]\n{doc['text']}")
    context = "\n\n---\n\n".join(context_parts)
    return f"Context from GraphXR documentation:\n\n{context}\n\n---\n\nQuestion: {question}"


def ask(client: OpenAI, question: str, context_docs: list[dict], stream: bool = True):
    user_prompt = build_prompt(question, context_docs)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    if stream:
        response = client.chat.completions.create(
            model=INFERENCE_MODEL,
            messages=messages,
            temperature=0.3,
            stream=True,
        )
        full_response = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                full_response += token
                console.print(token, end="", highlight=False)
        console.print()
        return full_response
    else:
        response = client.chat.completions.create(
            model=INFERENCE_MODEL,
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content


def interactive_mode(client: OpenAI, collection, top_k: int):
    console.print(Panel(
        "[bold blue]GraphXR Help Center RAG[/bold blue]\n"
        f"Inference: [cyan]{INFERENCE_MODEL}[/cyan] | "
        f"Embedding: [cyan]{EMBEDDING_MODEL}[/cyan]\n"
        "Type [bold]quit[/bold] or [bold]exit[/bold] to leave.",
        title="Interactive Mode",
    ))

    while True:
        try:
            question = console.input("\n[bold green]Question:[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nGoodbye!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            console.print("Goodbye!")
            break

        with console.status("Searching documentation..."):
            embedding = get_query_embedding(client, question, EMBEDDING_MODEL)
            docs = retrieve(collection, embedding, top_k)

        console.print(f"\n[dim]Retrieved {len(docs)} relevant chunks[/dim]")
        for i, doc in enumerate(docs, 1):
            score = f" (distance: {doc['distance']:.4f})" if doc["distance"] is not None else ""
            console.print(f"  [dim]{i}. {doc['source']}{score}[/dim]")

        console.print()
        ask(client, question, docs, stream=True)


def single_query(client: OpenAI, collection, question: str, show_sources: bool, top_k: int):
    embedding = get_query_embedding(client, question, EMBEDDING_MODEL)
    docs = retrieve(collection, embedding, top_k)

    if show_sources:
        console.print(f"[dim]Retrieved {len(docs)} relevant chunks:[/dim]")
        for i, doc in enumerate(docs, 1):
            score = f" (distance: {doc['distance']:.4f})" if doc["distance"] is not None else ""
            console.print(f"  [dim]{i}. {doc['source']}{score}[/dim]")
        console.print()

    answer = ask(client, question, docs, stream=True)
    return answer


def main():
    parser = argparse.ArgumentParser(description="Query the GraphXR Help Center RAG pipeline")
    parser.add_argument("question", nargs="?", help="Question to ask (omit for interactive mode)")
    parser.add_argument("--no-sources", action="store_true", help="Hide source documents")
    parser.add_argument("--top-k", type=int, default=TOP_K, help=f"Number of chunks to retrieve (default: {TOP_K})")
    args = parser.parse_args()

    if not CHROMA_DIR.exists():
        console.print("[red]Error: Vector store not found. Run ingest.py first.[/red]")
        sys.exit(1)

    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        collection = chroma_client.get_collection(COLLECTION_NAME)
    except Exception:
        console.print("[red]Error: Collection not found. Run ingest.py first.[/red]")
        sys.exit(1)

    client = OpenAI(base_url=LM_STUDIO_BASE_URL, api_key=LM_STUDIO_API_KEY)
    top_k = args.top_k

    if args.question:
        single_query(client, collection, args.question, show_sources=not args.no_sources, top_k=top_k)
    else:
        interactive_mode(client, collection, top_k=top_k)


if __name__ == "__main__":
    main()
