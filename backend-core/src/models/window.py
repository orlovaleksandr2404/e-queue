from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
from src.models.service import Service

window_services = Table(
    "window_services",
    Base.metadata,
    Column("window_id", ForeignKey("windows.id", ondelete="CASCADE"), primary_key=True),
    Column("service_id", ForeignKey("services.id", ondelete="CASCADE"), primary_key=True),
)

class Window(Base):
    __tablename__ = "windows"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    services: Mapped[list["Service"]] = relationship(
        "Service", secondary=window_services, lazy="selectin"
    )
