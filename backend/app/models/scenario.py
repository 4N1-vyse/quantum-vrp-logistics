from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    transport_mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    route_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
