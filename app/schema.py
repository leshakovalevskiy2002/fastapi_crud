from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime


class PostUpsert(BaseModel):
    title: Annotated[
        str,
        Field(
            min_length=5,
            max_length=100
        )
    ]
    content: Annotated[str, Field(max_length=1000)]
    is_draft: Annotated[bool, Field(default=False)]
    category_id: int


class Post(BaseModel):
    id: Annotated[int, Field(gt=0)]
    title: str
    slug: str
    content: str
    date_created: datetime
    date_updated: Annotated[
        datetime | None,
        Field(default_factory=datetime.now)
    ]
    is_draft: bool
    category_id: int

    class Config:
        from_attributes = True


class Category(BaseModel):
    id: int
    name: str
    is_active: bool


class CategoryUpsert(BaseModel):
    name: Annotated[str, Field(max_length=100)]