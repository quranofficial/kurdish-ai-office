from pydantic import BaseModel, Field

class AssistantRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    agent_key: str | None = Field(default=None, pattern=r"^[a-z_]{2,40}$")
