from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class Passage(Base):
    __tablename__ = "passages"

    passage_id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True
    )

    route_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("routes.route_id"),
        nullable=False
    )
