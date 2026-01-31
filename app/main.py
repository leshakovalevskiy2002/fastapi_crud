from fastapi import FastAPI

from app.routers import posts, categories


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

app.include_router(posts.router)
app.include_router(categories.router)