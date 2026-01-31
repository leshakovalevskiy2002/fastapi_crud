from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    content: Mapped[str] = mapped_column(String(1000))
    date_created: Mapped[datetime | None]
    date_updated: Mapped[datetime | None] = mapped_column(onupdate=datetime.now)
    is_draft: Mapped[bool | None]
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Category"] = relationship(
        back_populates="posts",
        uselist=False
    )