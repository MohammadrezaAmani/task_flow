from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from tortoise.queryset import Q

from src.app.common import Category, CategoryCreateScheme, CategoryResponseScheme
from src.helper import (
    ActionEnum,
    Filter,
    OrderBy,
    Paginated,
    Paginator,
    Status,
    create_filter_schema,
    log_action,
    login_required,
)

router = APIRouter()

CategoryFilterSchema = create_filter_schema(Category)


@router.get(
    "/", response_model=Paginated[CategoryResponseScheme] | List[CategoryResponseScheme]
)
@log_action(action=ActionEnum.VIEW.value, model=Category._meta.db_table)
async def get_categorys_router(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    filters: CategoryFilterSchema = Depends(),  # type: ignore
    user=Depends(login_required),
    sort_by: list[str] = Query([]),
    pagination: bool = Query(True),
):
    objects = Category.all()
    sort = OrderBy.create(objects, sort_by)
    objects = Filter.create(sort, filters)
    return await Paginator(limit=limit, page=page).paginated(
        CategoryResponseScheme, objects, apply=pagination
    )


@router.post("/", response_model=CategoryResponseScheme)
@log_action(action=ActionEnum.CREATE.value, model=Category._meta.db_table)
async def create_category_router(
    object: CategoryCreateScheme,
    user=Depends(login_required),
):
    return await object.create(
        Category,
        serialize=True,
        serializer=CategoryResponseScheme,
        m2m=[],
    )


@router.get("/{id}", response_model=CategoryResponseScheme)
@log_action(action=ActionEnum.VIEW.value, model=Category._meta.db_table)
async def get_category_router(
    id: str,
    request: Request,
    user=Depends(login_required),
):
    objects = Category.all()
    return await CategoryResponseScheme.from_tortoise_orm(
        CategoryResponseScheme,
        await objects.get(Q(id=id) if str(id).isdigit() else Q(slug=str(id))),
    )


@router.put("/{id}", response_model=CategoryResponseScheme)
@log_action(action=ActionEnum.UPDATE.value, model=Category._meta.db_table)
async def update_category_router(
    id: int,
    object: CategoryCreateScheme,
    user=Depends(login_required),
):
    objects = Category.all()
    return await object.update(
        await objects.get(id=id),
        serialize=True,
        serializer=CategoryResponseScheme,
        m2m=[],
    )


@router.delete("/{id}", response_model=Status)
@log_action(action=ActionEnum.DELETE.value, model=Category._meta.db_table)
async def delete_category_router(id: int):
    objects = Category.all()
    deleted_count = await objects.filter(id=id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Category {id} not found")
    return Status(message=f"Deleted category {id}")
