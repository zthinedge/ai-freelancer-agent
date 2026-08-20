import asyncio
import hashlib
import json
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app.agent.ports import ContextMemory
from app.agent.schemas import RetrievedContext

_ASCII_WORD = re.compile(r"[a-z0-9][a-z0-9_-]*")
_CJK_RUN = re.compile(r"[\u3400-\u9fff]+")


class SQLiteContextMemory(ContextMemory):
    """Local lexical RAG store optimized for small Chinese/English knowledge bases."""

    def __init__(self, database_path: Path, seed_directory: Path | None = None) -> None:
        self._database_path = database_path
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_lock = asyncio.Lock()
        self._initialize()
        if seed_directory is not None:
            self._seed_directory(seed_directory)

    async def search(self, query: str, limit: int = 3) -> tuple[RetrievedContext, ...]:
        bounded_limit = max(1, min(limit, 5))
        return await asyncio.to_thread(self._search, query, bounded_limit)

    async def remember(
        self,
        *,
        source_id: str,
        title: str,
        content: str,
        metadata: dict[str, str] | None = None,
    ) -> None:
        async with self._write_lock:
            await asyncio.to_thread(
                self._remember,
                source_id,
                title,
                content,
                metadata or {},
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge_chunks(source_id)"
            )
            connection.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                    chunk_id UNINDEXED,
                    search_text,
                    tokenize='unicode61'
                )
                """
            )

    def _remember(
        self,
        source_id: str,
        title: str,
        content: str,
        metadata: dict[str, str],
    ) -> None:
        normalized_content = content.strip()
        if not source_id.strip() or not title.strip() or not normalized_content:
            raise ValueError("memory source_id, title and content must not be empty")
        chunks = _chunk_text(normalized_content)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            old_rows = connection.execute(
                "SELECT id FROM knowledge_chunks WHERE source_id = ?",
                (source_id,),
            ).fetchall()
            for row in old_rows:
                connection.execute("DELETE FROM knowledge_fts WHERE chunk_id = ?", (row["id"],))
            connection.execute("DELETE FROM knowledge_chunks WHERE source_id = ?", (source_id,))
            for index, chunk in enumerate(chunks):
                chunk_id = hashlib.sha256(f"{source_id}:{index}:{chunk}".encode()).hexdigest()
                connection.execute(
                    """
                    INSERT INTO knowledge_chunks(
                        id, source_id, title, content, metadata, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chunk_id,
                        source_id,
                        title.strip(),
                        chunk,
                        json.dumps(metadata, ensure_ascii=False, sort_keys=True),
                        datetime.now(UTC).isoformat(),
                    ),
                )
                connection.execute(
                    "INSERT INTO knowledge_fts(chunk_id, search_text) VALUES (?, ?)",
                    (chunk_id, " ".join(_tokenize(f"{title} {chunk}"))),
                )

    def _search(self, query: str, limit: int) -> tuple[RetrievedContext, ...]:
        query_tokens = tuple(dict.fromkeys(_tokenize(query)))
        if not query_tokens:
            return ()
        match_expression = " OR ".join(f'"{token}"' for token in query_tokens[:40])
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT c.source_id, c.title, c.content, f.search_text, bm25(knowledge_fts) rank
                FROM knowledge_fts f
                JOIN knowledge_chunks c ON c.id = f.chunk_id
                WHERE knowledge_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (match_expression, limit * 4),
            ).fetchall()
        query_set = set(query_tokens)
        results: list[RetrievedContext] = []
        seen_sources: set[str] = set()
        for row in rows:
            if row["source_id"] in seen_sources:
                continue
            seen_sources.add(row["source_id"])
            results.append(
                RetrievedContext(
                    source_id=row["source_id"],
                    title=row["title"],
                    excerpt=row["content"][:1200],
                    score=round(min(1.0, _overlap_score(query_set, row["search_text"])), 4),
                )
            )
            if len(results) >= limit:
                break
        return tuple(results)

    def _seed_directory(self, directory: Path) -> None:
        if not directory.exists():
            return
        for path in sorted(directory.glob("*.md")):
            content = path.read_text(encoding="utf-8").strip()
            if not content:
                continue
            first_line = content.splitlines()[0].lstrip("# ").strip()
            self._remember(
                f"knowledge:{path.stem}",
                first_line or path.stem,
                content,
                {"kind": "curated_knowledge", "path": path.name},
            )


def _tokenize(text: str) -> list[str]:
    normalized = text.lower()
    tokens = _ASCII_WORD.findall(normalized)
    for run in _CJK_RUN.findall(normalized):
        if len(run) == 1:
            tokens.append(run)
        else:
            tokens.extend(run[index : index + 2] for index in range(len(run) - 1))
    return tokens


def _chunk_text(text: str, max_chars: int = 900) -> tuple[str, ...]:
    paragraphs = [
        paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()
    ]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(
                paragraph[index : index + max_chars]
                for index in range(0, len(paragraph), max_chars)
            )
        elif not current:
            current = paragraph
        elif len(current) + len(paragraph) + 2 <= max_chars:
            current = f"{current}\n\n{paragraph}"
        else:
            chunks.append(current)
            current = paragraph
    if current:
        chunks.append(current)
    return tuple(chunks)


def _overlap_score(query_tokens: set[str], search_text: str) -> float:
    return len(query_tokens.intersection(search_text.split())) / len(query_tokens)
