import sqlite3
from pathlib import Path

from app.core.models.response_models import LLMResponse

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "storage" / "responses.db"
class ResponseStore:

    def __init__(self):

        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()

        self.create_table()
        print("data_base_path:", DB_PATH)

    def create_table(self):

        self.cursor.execute("""
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
            """)

        self.connection.commit()

    def add_response(self, response: LLMResponse):

        self.cursor.execute(
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

        self.connection.commit()

        return {"status": "stored", "cache_id": str(response.cache_id)}
