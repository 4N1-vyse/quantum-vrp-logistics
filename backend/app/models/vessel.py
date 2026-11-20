from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class Vessel(Base):
    __tablename__ = "vessels"

    vessel_id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True
    )

    type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    capacity_t: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    speed_kn: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    is_synthetic: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )
