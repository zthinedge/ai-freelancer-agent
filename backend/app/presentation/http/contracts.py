from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str
    environment: str
    architecture: Literal["modular-monolith"] = "modular-monolith"
