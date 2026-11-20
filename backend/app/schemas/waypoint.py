from pydantic import BaseModel, ConfigDict


class WaypointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    passage_id: str
    seq: int
    waypoint_name: str
    lat_deg: float
    lon_deg: float
