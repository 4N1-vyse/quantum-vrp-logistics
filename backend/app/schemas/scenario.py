from typing import Literal
from pydantic import BaseModel, Field


class ScenarioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    transport_mode: Literal["maritime", "air"]
    route_id: str = Field(min_length=1)

class ScenarioResponse(BaseModel):
    id: str
    name: str
    transport_mode: Literal["maritime", "air"]
    route_id: str
