from pydantic import BaseModel, ConfigDict


class VesselResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vessel_id: str
    type: str
    capacity_t: float
    speed_kn: float
    is_synthetic: bool
