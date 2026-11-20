from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ShipmentCreate(BaseModel):
    shipment_id: str = Field(min_length=1, max_length=20)
    transport_mode: Literal["maritime"]
    route_id: str = Field(min_length=1, max_length=50)
    weight_t: float = Field(gt=0)
    earliest_departure_utc: datetime
    deadline_utc: datetime
    is_synthetic: bool = True

    @field_validator("earliest_departure_utc", "deadline_utc")
    @classmethod
    def validate_utc_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime must include timezone information")

        return value.astimezone(timezone.utc)

    @field_validator("deadline_utc")
    @classmethod
    def validate_deadline(
        cls,
        value: datetime,
        info,
    ) -> datetime:
        departure = info.data.get("earliest_departure_utc")

        if departure is not None and value <= departure:
            raise ValueError("Deadline must be after earliest departure")

        return value


class ShipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    shipment_id: str
    transport_mode: str
    route_id: str
    weight_t: float
    earliest_departure_utc: datetime
    deadline_utc: datetime
    is_synthetic: bool
