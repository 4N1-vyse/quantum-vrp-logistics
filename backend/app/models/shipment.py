from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    shipment_id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True
    )

    transport_mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    route_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    weight_t: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    earliest_departure_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    deadline_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    is_synthetic: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )
