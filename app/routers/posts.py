from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence, Annotated

from app.routers.categories import get_category_or_404
from app.schema import Post as PostSchema, PostUpsert
from app.models import Post as PostModel, Category as CategoryModel
from app.db_depends import get_async_db


router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


async def get_all_posts(db: AsyncSession) -> Sequence[PostModel]:
    db_posts = await db.scalars(select(PostModel).where(
        PostModel.is_draft == False)
    )
    return db_posts.all()


async def get_post_or_404(post_id: int, db: AsyncSession):
    result = await db.scalars(
        select(PostModel).where(
            PostModel.id == post_id,
            PostModel.is_draft == False
        )
    )
    post_db = result.first()

    if post_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post_db


async def check_body_request_data(cat_id, db: AsyncSession):
    cat_result = await db.scalars(
        select(CategoryModel).where(
            CategoryModel.id == cat_id,
            CategoryModel.is_active == True
        )
    )
    cat_db = cat_result.first()

    if cat_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The category doesn't exist"
        )


@router.get("", response_model=list[PostSchema])
async def read_posts(
        db: Annotated[AsyncSession, Depends(get_async_db)]
) -> Sequence[PostSchema]:
    return await get_all_posts(db)


@router.get("/{post_id}", response_model=PostSchema)
async def read_post(
        post_id: int,
        db: Annotated[AsyncSession, Depends(get_async_db)]
) -> PostSchema:
    return await get_post_or_404(post_id, db)


@router.get("/category/{cat_id}")
async def get_posts_by_category(
        cat_id: int,
        db: Annotated[AsyncSession, Depends(get_async_db)]
):
    _ = await get_category_or_404(cat_id, db)

    posts = await db.scalars(
        select(PostModel).where(
            PostModel.category_id == cat_id,
            PostModel.is_draft == False
        )
    )
    return posts.all()


@router.post("",
          status_code=status.HTTP_201_CREATED,
          response_model=PostSchema)
async def create_post(
        new_post: PostUpsert,
        db: Annotated[AsyncSession, Depends(get_async_db)]
) -> PostSchema:
    category_id = new_post.category_id
    await check_body_request_data(category_id, db)

    slug = slugify(new_post.title)
    date_created = datetime.now()

    post_db = PostModel(slug=slug,
                        date_created=date_created,
                        date_updated=None,
                        **new_post.model_dump())
    try:
        db.add(post_db)
        await db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post with this title already exists"
        )
    return post_db


@router.put("/{post_id}", response_model=PostSchema)
async def update_post(
        post_id: int,
        updated_post: PostUpsert,
        db: Annotated[AsyncSession, Depends(get_async_db)]
) -> PostSchema:
    db_post = await get_post_or_404(post_id, db)

    category_id = updated_post.category_id
    await check_body_request_data(category_id, db)

    db_post.slug = slugify(updated_post.title)

    for attr, value in updated_post.model_dump().items():
        setattr(db_post, attr, value)

    try:
        await db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post with this title already exists"
        )
    return db_post


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(
        post_id: int,
        db: Annotated[AsyncSession, Depends(get_async_db)]
) -> str:
    db_post = await get_post_or_404(post_id, db)
    db_post.is_draft = True
    await db.commit()
    return f"Post {post_id} was deleted!"


@router.delete("", status_code=status.HTTP_200_OK)
async def delete_posts(
        db: Annotated[AsyncSession, Depends(get_async_db)]
) -> str:
    db_posts = await get_all_posts(db)
    for post in db_posts:
        post.is_draft = True
    await db.commit()
    return "All posts deleted!"