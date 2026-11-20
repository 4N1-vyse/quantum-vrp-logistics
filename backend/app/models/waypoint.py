from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class Waypoint(Base):
    __tablename__ = "waypoints"

    __table_args__ = (
        UniqueConstraint(
            "passage_id",
            "seq",
            name="uq_waypoint_passage_sequence"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    passage_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("passages.passage_id"),
        nullable=False
    )

    seq: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    waypoint_name: Mapped[str] = mapped_column(
        String(100),
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
