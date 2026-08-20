import asyncio
import json
import sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from app.application.contracts import AgentRunView, ProjectView
from app.application.ports import ProjectAnalysisStore


def sqlite_path_from_url(database_url: str) -> Path:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise ValueError("当前版本只支持 sqlite:/// 数据库地址")
    raw_path = database_url[len(prefix) :]
    if not raw_path or raw_path == ":memory:":
        raise ValueError("持久化Memory需要文件型SQLite地址，不能使用空路径或:memory:")
    return Path(raw_path).expanduser().resolve()


class SQLiteProjectAnalysisStore(ProjectAnalysisStore):
    """Persist complete project and AgentState snapshots as versioned JSON."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_lock = asyncio.Lock()
        self._initialize()

    async def save_project(self, project: ProjectView) -> None:
        async with self._write_lock:
            await asyncio.to_thread(self._save_project, project)

    async def save_run(self, run: AgentRunView) -> None:
        async with self._write_lock:
            await asyncio.to_thread(self._save_run, run)

    async def get_run(self, run_id: UUID) -> AgentRunView | None:
        return await asyncio.to_thread(self._get_run, run_id)

    async def get_project(self, project_id: UUID) -> ProjectView | None:
        return await asyncio.to_thread(self._get_project, project_id)

    async def list_projects(self) -> Sequence[ProjectView]:
        return await asyncio.to_thread(self._list_projects)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    run_id TEXT UNIQUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at DESC)"
            )

    def _save_project(self, project: ProjectView) -> None:
        payload = project.model_dump_json()
        run_id = str(project.run.id) if project.run else None
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO projects(id, run_id, created_at, updated_at, payload)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    run_id=excluded.run_id,
                    updated_at=excluded.updated_at,
                    payload=excluded.payload
                """,
                (
                    str(project.id),
                    run_id,
                    project.created_at.isoformat(),
                    project.updated_at.isoformat(),
                    payload,
                ),
            )

    def _save_run(self, run: AgentRunView) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT payload FROM projects WHERE run_id = ?",
                (str(run.id),),
            ).fetchone()
            if row is None:
                raise KeyError(f"project for run {run.id} does not exist")
            project = ProjectView.model_validate_json(row["payload"])
            updated_at = datetime.now(UTC)
            updated_project = project.model_copy(update={"run": run, "updated_at": updated_at})
            connection.execute(
                "UPDATE projects SET updated_at = ?, payload = ? WHERE id = ?",
                (
                    updated_at.isoformat(),
                    updated_project.model_dump_json(),
                    str(project.id),
                ),
            )

    def _get_run(self, run_id: UUID) -> AgentRunView | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM projects WHERE run_id = ?",
                (str(run_id),),
            ).fetchone()
        if row is None:
            return None
        return ProjectView.model_validate_json(row["payload"]).run

    def _get_project(self, project_id: UUID) -> ProjectView | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM projects WHERE id = ?",
                (str(project_id),),
            ).fetchone()
        return None if row is None else ProjectView.model_validate_json(row["payload"])

    def _list_projects(self) -> tuple[ProjectView, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM projects ORDER BY created_at DESC"
            ).fetchall()
        return tuple(ProjectView.model_validate(json.loads(row["payload"])) for row in rows)
