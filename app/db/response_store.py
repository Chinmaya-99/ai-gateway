import aiosqlite
from pathlib import Path

from app.models.response_models import LLMResponse

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "storage" / "responses.db"


class ResponseStore:

    def __init__(self):
        self.db_path = DB_PATH
        self.connection: aiosqlite.Connection | None = None

    @classmethod
    async def create(cls) -> "ResponseStore":
        instance = cls()
        await instance._initialize()
        return instance

    async def _initialize(self):
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self.create_table()
        print("data_base_path:", self.db_path)

    async def create_table(self):
        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                cache_id TEXT PRIMARY KEY,
                provider TEXT,
                model TEXT,
                answer TEXT,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                created_at TEXT
            )
            """
        )
        await self.connection.commit()

    async def add_response(self, response: LLMResponse) -> dict:
        print ("Storing response in database:")
        await self.connection.execute(
            """
            INSERT INTO responses VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                str(response.cache_id),
                response.provider,
                response.model,
                response.answer,
                response.prompt_tokens,
                response.completion_tokens,
                response.total_tokens,
                str(response.created_at),
            ),
        )
        await self.connection.commit()
        return {"status": "stored", "cache_id": str(response.cache_id)}

    async def get_response(self, cache_id: str) -> dict | None:
        async with self.connection.execute(
            "SELECT * FROM responses WHERE cache_id = ?",
            (cache_id,),
        ) as cursor:
            row = await cursor.fetchone()

        if row:
            return {
                "cache_id": row["cache_id"],
                "provider": row["provider"],
                "model": row["model"],
                "answer": row["answer"],
                "prompt_tokens": row["prompt_tokens"],
                "completion_tokens": row["completion_tokens"],
                "total_tokens": row["total_tokens"],
                "created_at": row["created_at"],
            }
        return None

    async def close(self):
        if self.connection:
            await self.connection.close()
