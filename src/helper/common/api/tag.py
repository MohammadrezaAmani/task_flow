from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from tortoise.queryset import Q

from src.app.common import Tag, TagCreateScheme, TagResponseScheme
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

TagFilterSchema = create_filter_schema(Tag)


@router.get("/", response_model=Paginated[TagResponseScheme] | List[TagResponseScheme])
@log_action(action=ActionEnum.VIEW.value, model=Tag._meta.db_table)
async def get_tags_router(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    filters: TagFilterSchema = Depends(),  # type: ignore
    user=Depends(login_required),
    sort_by: list[str] = Query([]),
    pagination: bool = Query(True),
):
    objects = Tag.all()
    sort = OrderBy.create(objects, sort_by)
    objects = Filter.create(sort, filters)
    return await Paginator(limit=limit, page=page).paginated(
        TagResponseScheme, objects, apply=pagination
    )


@router.post("/", response_model=TagResponseScheme)
@log_action(action=ActionEnum.CREATE.value, model=Tag._meta.db_table)
async def create_tag_router(
    object: TagCreateScheme,
    user=Depends(login_required),
):
    return await object.create(
        Tag,
        serialize=True,
        serializer=TagResponseScheme,
        m2m=[],
    )


@router.get("/{id}", response_model=TagResponseScheme)
@log_action(action=ActionEnum.VIEW.value, model=Tag._meta.db_table)
async def get_tag_router(
    id: str,
    request: Request,
    user=Depends(login_required),
):
    objects = Tag.all()
    return await TagResponseScheme.from_tortoise_orm(
        TagResponseScheme,
        await objects.get(Q(id=id) if str(id).isdigit() else Q(slug=str(id))),
    )


@router.put("/{id}", response_model=TagResponseScheme)
@log_action(action=ActionEnum.UPDATE.value, model=Tag._meta.db_table)
async def update_tag_router(
    id: int,
    object: TagCreateScheme,
    user=Depends(login_required),
):
    objects = Tag.all()
    return await object.update(
        await objects.get(id=id),
        serialize=True,
        serializer=TagResponseScheme,
        m2m=[],
    )


@router.delete("/{id}", response_model=Status)
@log_action(action=ActionEnum.DELETE.value, model=Tag._meta.db_table)
async def delete_tag_router(id: int):
    objects = Tag.all()
    deleted_count = await objects.filter(id=id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Tag {id} not found")
    return Status(message=f"Deleted tag {id}")
