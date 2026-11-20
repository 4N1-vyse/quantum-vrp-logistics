from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class Route(Base):
    __tablename__ = "routes"

    route_id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True
    )

    origin: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("locations.location_id"),
        nullable=False
    )

    destination: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("locations.location_id"),
        nullable=False
    )
