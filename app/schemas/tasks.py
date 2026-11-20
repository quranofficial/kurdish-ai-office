from typing import Literal
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    description: str = Field(default="", max_length=8000)
    priority: Literal["low", "normal", "high", "urgent"] = "normal"

class TaskPlan(BaseModel):
    agent_key: str
    agent_name: str
    reason: str
    requires_approval: bool
    status: str = "planned"
