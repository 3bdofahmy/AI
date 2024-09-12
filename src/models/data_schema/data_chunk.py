from pydantic import BaseModel, Field
from typing import Dict

class DataChunk(BaseModel):
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: Dict  
    chunk_order: int = Field(..., gt=0)


class RetrievedDocument(BaseModel):
    text: str
    score: float