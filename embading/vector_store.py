import chromadb
from pydantic_datatypes import EmbeddingModelData
import uuid
from pathlib import Path

class VectorStore:
    def __init__(self):
        base_dire=Path(__file__).parent

        self.client = chromadb.PersistentClient(
            path=str(base_dire/"chromadb_data")
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
