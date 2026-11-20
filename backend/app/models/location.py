from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class Location(Base):
    __tablename__ = "locations"

    location_id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    lat_deg: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    lon_deg: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
