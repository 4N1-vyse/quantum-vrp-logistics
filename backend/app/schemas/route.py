from pydantic import BaseModel, ConfigDict


class RouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    route_id: str
    origin: str
    destination: str
