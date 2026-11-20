from pydantic import BaseModel, ConfigDict


class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location_id: str
    name: str
    type: str
    lat_deg: float
    lon_deg: float
    source: str
