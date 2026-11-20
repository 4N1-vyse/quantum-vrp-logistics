from pydantic import BaseModel, ConfigDict


class PassageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    passage_id: str
    route_id: str
