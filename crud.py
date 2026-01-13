from fastapi import FastAPI, HTTPException, status
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


@app.get("/posts", tags=["posts"],
         response_model=list[Post])
async def read_posts() -> list[Post]:
    return posts_db


@app.get("/posts/{post_id}", tags=["posts"],
         response_model=Post)
async def read_post(post_id: int) -> Post:
    for post in posts_db:
        if post.id == post_id:
            return post
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found"
    )


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
        post_id: int,
        updated_post: PostUpsert
) -> Post:
    for i, post in enumerate(posts_db):
        if post.id == post_id:
            new_post = Post(id=post_id, date_created=post.date_created, **updated_post.model_dump())
            posts_db[i] = new_post
            return new_post
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found"
    )


@app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK,
            tags=["posts"])
async def delete_post(post_id: int) -> dict[str, str]:
    for i, post in enumerate(posts_db):
        if post.id == post_id:
            del posts_db[i]
            return {"detail": f"Post {post_id} was deleted!"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found"
    )


@app.delete("/posts", status_code=status.HTTP_200_OK, tags=["posts"])
async def delete_posts() -> dict[str, str]:
    posts_db.clear()
    return {"detail": "All posts deleted!"}