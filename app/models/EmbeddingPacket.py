import numpy as np
from pydantic import BaseModel, model_validator

class EmbeddingPacket(BaseModel):
    query: str
    vector: list[float]
    norm: float = 0.0
    magnitude: float = 0.0

    model_config = {"arbitrary_types_allowed": True}

    @model_validator(mode="after")
    def compute_stats(self) -> "EmbeddingPacket":
        arr = np.array(self.vector)
        self.norm = float(np.linalg.norm(arr))
        self.magnitude = float(np.mean(np.abs(arr)))
        return self