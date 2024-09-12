from pydantic import BaseModel, Field

class Project(BaseModel):
    project_id: str = Field(..., min_length=1)

    