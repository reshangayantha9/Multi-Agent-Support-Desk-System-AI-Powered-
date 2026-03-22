from __future__ import annotations
import os
import logging
import re
import asyncio
from pathlib import Path
from typing import Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient, models as qmodels

from app.config.settings import get_settings
settings = get_settings()

os.environ["OPENAI_API_KEY"] = settings.openai_api_key

logger = logging.getLogger(__name__)
settings = get_settings()

_qdrant: QdrantClient | None = None
_embeddings: OpenAIEmbeddings | None = None

def get_qdrant() -> QdrantClient:
    global _qdrant
    if _qdrant is None:
        if settings.qdrant_in_memory:
            _qdrant = QdrantClient(":memory:")
        else:
            _qdrant = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port, check_compatibility=False)
    logger.info(f"[RAG][QDRANT] Initialized remote client at {settings.qdrant_host}:{settings.qdrant_port}")
    return _qdrant

def get_embeddings() -> OpenAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
        )
    logger.info(f"[RAG][EMBEDDINGS] Initialized model={settings.embedding_model}")
    return _embeddings


def _chunk_text(text: str, chunk_size: int = 512, chunk_overlap: int = 50) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n## ", "\n\n### ", "\n\n", "\n", " ", ""],
        length_function=len,
    )
    return splitter.split_text(text)


async def index_kb(kb_path: str | None = None) -> int:
    project_root = Path(__file__).parent.parent.parent
    raw_path = kb_path or settings.kb_docs_path
    kb_dir = (project_root / raw_path).resolve()

    logger.info(f"[RAG][INDEX][START] path={kb_dir}")
    qdrant = get_qdrant()
    emb = get_embeddings()

    if qdrant.collection_exists(settings.qdrant_collection):
        collection_info = qdrant.get_collection(settings.qdrant_collection)
        if collection_info.points_count > 0:
            logger.info(f"[RAG][INDEX][SKIP] Collection exists with {collection_info.points_count} chunks")
            return collection_info.points_count
    else:
        logger.info(f"[RAG][INDEX][CREATE] Creating collection '{settings.qdrant_collection}'")
        qdrant.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=qmodels.VectorParams(size=1536, distance=qmodels.Distance.COSINE),
        )

    all_chunks = []
    metadata_list = []

    for md_file in sorted(kb_dir.glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")

        m = re.search(r"\*\*doc_id:\s*([\w-]+)\*\*", raw)
        doc_id_tag = m.group(1) if m else md_file.stem.upper()

        chunks = _chunk_text(raw, settings.rag_chunk_size, settings.rag_chunk_overlap)
        logger.info(f"[RAG][INDEX][CHUNK] {md_file.name} -> {len(chunks)} chunks | doc_id={doc_id_tag}")

        for idx, text in enumerate(chunks):
            all_chunks.append(text)
            metadata_list.append({
                "doc_id": doc_id_tag,
                "chunk_id": idx,
                "text": text,
                "source_file": md_file.name
            })

    if not all_chunks:
        return 0

    logger.info(f"[RAG][INDEX][EMBED] Embedding {len(all_chunks)} chunks in batch...")
    vectors = await _embed_batch_async(emb, all_chunks)
    logger.info(f"[RAG][INDEX][EMBED] Generated {len(vectors)} embeddings")

    points = [
        qmodels.PointStruct(
            id=i,
            vector=vector,
            payload=metadata_list[i]
        )
        for i, vector in enumerate(vectors)
    ]

    qdrant.upsert(collection_name=settings.qdrant_collection, points=points)

    logger.info(f"KB indexing complete: {len(points)} total chunks saved")
    return len(points)


async def _embed_batch_async(emb: OpenAIEmbeddings, texts: list[str]) -> list[list[float]]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: emb.embed_documents(texts))

async def _embed_async(emb: OpenAIEmbeddings, text: str) -> list[float]:

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, emb.embed_query, text)

async def search_kb(query: str) -> list[dict[str, Any]]:
    logger.info(f"[RAG][SEARCH][START] query='{query}'")
    emb = get_embeddings()
    qdrant = get_qdrant()

    query_vector = await _embed_async(emb, query)

    results = qdrant.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        limit=settings.rag_top_k,
        with_payload=True,
    )

    return [
        {
            "doc_id": point.payload["doc_id"],
            "chunk_id": point.payload["chunk_id"],
            "text": point.payload["text"],
            "score": round(point.score, 4),
        }
        for point in results.points
    ]