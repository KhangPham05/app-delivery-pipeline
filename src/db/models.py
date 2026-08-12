from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base


class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    short_code: Mapped[str] = mapped_column(String(6), unique=True, nullable=False)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    clicks: Mapped[list["Click"]] = relationship(back_populates="url")


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    url_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("urls.id"), nullable=False)
    clicked_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    url: Mapped["Url"] = relationship(back_populates="clicks")
