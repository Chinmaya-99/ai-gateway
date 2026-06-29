from pathlib import Path
import chromadb

PROJECT_ROOT = Path(__file__).resolve()

while PROJECT_ROOT.name != "ai_gateway":
    PROJECT_ROOT = PROJECT_ROOT.parent

CHROMA_PATH = PROJECT_ROOT / "storage" / "chromadb"


class SemanticCache:

    def __init__(self):
        self.client: chromadb.AsyncClientAPI | None = None
        self.collection = None

    @classmethod
    async def create(cls) -> "SemanticCache":
        instance = cls()
        await instance._initialize()
        return instance

    async def _initialize(self):
        self.client = await chromadb.AsyncPersistentClient(path=str(CHROMA_PATH))
        self.collection = await self.client.get_or_create_collection(name="embeddings")
        print("CACHE PATH:", CHROMA_PATH)
        print("CACHE COLLECTION:", self.collection.name)
        print(self.collection.metadata)

    async def search_similar(
        self, query_embedding: list[float], n_results: int = 1
    ) -> dict | None:

        results = await self.collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )
        print("\nRAW RESULTS:")
        print(results)

        if not results["ids"][0]:
            return None

        cache_id = results["ids"][0][0]
        distance = results["distances"][0][0]
        similarity = 1 - distance

        return {"cache_id": cache_id, "similarity": similarity}
