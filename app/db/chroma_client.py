import chromadb
import uuid
from pathlib import Path

from app.core.models.cache_models import EmbeddingModelData

class VectorStore:
    def __init__(self):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent

        CHROMA_PATH = BASE_DIR / "storage" / "chromadb"

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )

        self.collection = (
            self.client.get_or_create_collection(
                name="embeddings"
            )
        )

    def add_documents(self, data: EmbeddingModelData):
        unique_id = str(uuid.uuid4())
        self.collection.add(
            documents=[data.text], embeddings=[data.embedding], ids=[unique_id]
        )
        return {
            "status": "success",
            "message": f"Document added with ID: {unique_id}",
        }
