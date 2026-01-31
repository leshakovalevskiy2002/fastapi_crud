from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db_depends import get_async_db
from app.models import Category as CategoryModel
from app.schema import Category as CategorySchema, CategoryUpsert


router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


async def get_category_or_404(
        cat_id: int,
        db: AsyncSession
) -> CategoryModel:
    cat_result = await db.scalars(
        select(CategoryModel).where(
            CategoryModel.is_active == True,
            CategoryModel.id == cat_id
        )
    )
    cat_db = cat_result.first()

    if cat_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category doesn't exist"
        )
    return cat_db


@router.get("", response_model=list[CategorySchema])
async def get_all_categories(
        db: Annotated[AsyncSession, Depends(get_async_db)]
) -> Sequence[CategoryModel]:
    db_posts = await db.scalars(
        select(CategoryModel).where(
            CategoryModel.is_active == True
        )
    )
    return db_posts.all()


@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=CategorySchema)
async def create_category(
        new_category: CategoryUpsert,
        db: Annotated[AsyncSession, Depends(get_async_db)]
):
    db_category = CategoryModel(**new_category.model_dump())
    db.add(db_category)
    await db.commit()
    return db_category


@router.get("/{cat_id}", response_model=CategorySchema)
async def get_category(
        cat_id: int,
        db: Annotated[AsyncSession, Depends(get_async_db)]
) -> CategorySchema:
    return await get_category_or_404(cat_id, db)


@router.put("/{cat_id}")
async def update_category(
        cat_id: int,
        updated_cat: CategoryUpsert,
        db: Annotated[AsyncSession, Depends(get_async_db)]
):
    cat_db = await get_category_or_404(cat_id, db)

    for attr, value in updated_cat.model_dump().items():
        setattr(cat_db, attr, value)

    await db.commit()
    return cat_db


@router.delete("/{cat_id}")
async def delete_category(
        cat_id: int,
        db: Annotated[AsyncSession, Depends(get_async_db)]
):
    cat_db = await get_category_or_404(cat_id, db)
    cat_db.is_active = False
    await db.commit()
    return {"detail": "Category was deleted"}