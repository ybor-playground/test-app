from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ItemModel(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String(8), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, default="")
