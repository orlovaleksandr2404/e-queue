from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    prefix: Mapped[str] = mapped_column(String(5), nullable=False)
    avg_duration_minutes: Mapped[int] = mapped_column(Integer, default=10)

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="service")
