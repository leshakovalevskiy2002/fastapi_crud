from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime


app = FastAPI(
    title="CRUD application",
    description="This CRUD application supports **writing**, **reading**,"
                "**updating** and **deleting** posts",
    version="0.0.1",
    openapi_tags=[
        {
            "name": "posts",
            "description": "CRUD operations which you can do with posts"
        }
    ],
    contact={
            "name": "leshakovalevskiy2002",
            "email": "lesha_programmer02_gt@mail.ru"
    }
)


class PostUpsert(BaseModel):
    title: Annotated[
        str,
        Field(
            min_length=5,
            max_length=100
        )
    ]
    slug: Annotated[
        str,
        Field(
            max_length=100,
            pattern="^[-_a-zA-Z0-9]*$"
        )
    ]
    content: Annotated[str, Field(max_length=1000)]
    is_draft: Annotated[bool, Field(default=False)]


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


posts_db: list[Post] = []


def get_post_or_404(post_id: int) -> tuple[int, Post]:
    for i, post in enumerate(posts_db):
        if post.id == post_id:
            return i, post
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found"
    )

FoundPost = Annotated[tuple[int, Post], Depends(get_post_or_404)]


@app.get("/posts", tags=["posts"],
         response_model=list[Post])
async def read_posts() -> list[Post]:
    return posts_db


@app.get("/posts/{post_id}", tags=["posts"],
         response_model=Post)
async def read_post(found_post: FoundPost) -> Post:
    return found_post[1]


@app.post("/posts", status_code=status.HTTP_201_CREATED,
          tags=["posts"], response_model=Post)
async def create_post(new_post: PostUpsert) -> Post:
    pk = max(post.id for post in posts_db) + 1 if posts_db else 1
    post = Post(id=pk, **new_post.model_dump(),
                date_created=datetime.now(), date_updated=None)
    posts_db.append(post)
    return post


@app.put("/posts/{post_id}", tags=["posts"],
         response_model=Post)
async def update_post(
        found_post: FoundPost,
        updated_post: PostUpsert
) -> Post:
    index, post = found_post
    new_post = Post(id=post.id, date_created=post.date_created, **updated_post.model_dump())
    posts_db[index] = new_post
    return new_post


@app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK,
            tags=["posts"])
async def delete_post(found_post: FoundPost) -> dict[str, str]:
    index, post = found_post
    del posts_db[index]
    return {"detail": f"Post {post.id} was deleted!"}


@app.delete("/posts", status_code=status.HTTP_200_OK, tags=["posts"])
async def delete_posts() -> dict[str, str]:
    posts_db.clear()
    return {"detail": "All posts deleted!"}