from pydantic import BaseModel, ConfigDict
from typing import Any


class QueryResponse(BaseModel):

    model_config = ConfigDict(
        extra="ignore"
    )

    success: bool
    intent: str

    value: Any | None = None
    title: str | None = None
    results: list | None = None
    message: str | None = None
    state: str | None = None
    availability: dict | None = None