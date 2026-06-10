import chromadb
from pathlib import Path

from ai_gateway.app.models.cache_models import EmbeddingModelData
PROJECT_ROOT = Path(__file__).resolve()

while PROJECT_ROOT.name != "ai_gateway":
    PROJECT_ROOT = PROJECT_ROOT.parent

CHROMA_PATH = PROJECT_ROOT / "storage" / "chromadb"

class VectorStore:
    def __init__(self):
       

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )

        self.collection = (
            self.client.get_or_create_collection(
                name="embeddings"
            )
        )
        print("VECTOR PATH:", CHROMA_PATH)
        print("VECTOR COLLECTION:", self.collection.name)

    def add_documents(self, data: EmbeddingModelData):
        self.collection.add(
            documents=[data.text], embeddings=[data.embedding], ids=[data.cache_id]
        )
        return {
            "status": "success",
            "message": f"Document added with ID: {data.cache_id}",
        }
