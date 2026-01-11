from fastapi import FastAPI, HTTPException, status, Body
from typing import Annotated


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


posts_db: dict[int, str] = {
    1: "My first post to work with FastAPI"
}


@app.get("/posts", tags=["posts"])
async def read_posts() -> dict[int, str]:
    return posts_db


@app.get("/posts/{post_id}", tags=["posts"])
async def read_post(post_id: int) -> str:
    try:
        return posts_db[post_id]
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )


@app.post("/posts", status_code=status.HTTP_201_CREATED, tags=["posts"])
async def create_post(
        post_message: Annotated[
            str,
            Body()
        ]
) -> str:
    index = max(posts_db) + 1 if posts_db else 1
    posts_db[index] = post_message
    return "Post created!"


@app.put("/posts/{post_id}", tags=["posts"])
async def update_post(
        post_id: int,
        post_message : Annotated[
            str,
            Body()
        ]
) -> str:
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    posts_db[post_id] = post_message

    return f"Post {post_id} was successfully updated"


@app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK, tags=["posts"])
async def delete_post(post_id: int) -> str:
    if post_id not in posts_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    del posts_db[post_id]

    return f"Post {post_id} was successfully deleted"

@app.delete("/posts", status_code=status.HTTP_200_OK, tags=["posts"])
async def delete_posts() -> str:
    posts_db.clear()
    return "All posts was successfully deleted"