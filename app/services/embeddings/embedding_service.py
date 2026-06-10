from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from ai_gateway.app.models.cache_models import EmbeddingModelData

load_dotenv()

class EmbeddingModel:
    def __init__(self):
        self.model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

    def embed_text(self, text: str, cache_id) -> EmbeddingModelData:
        embedding = self.model.embed_query(text)

        return EmbeddingModelData(
            cache_id=cache_id,
            text=text,
            embedding=embedding
        )
