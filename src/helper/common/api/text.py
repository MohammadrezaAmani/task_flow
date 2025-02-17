from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from tortoise.queryset import Q

from src.app.common import Text, TextCreateScheme, TextResponseScheme
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

TextFilterSchema = create_filter_schema(Text)


@router.get(
    "/", response_model=Paginated[TextResponseScheme] | List[TextResponseScheme]
)
@log_action(action=ActionEnum.VIEW.value, model=Text._meta.db_table)
async def get_texts_router(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    filters: TextFilterSchema = Depends(),  # type: ignore
    user=Depends(login_required),
    sort_by: list[str] = Query([]),
    pagination: bool = Query(True),
):
    objects = Text.all()
    sort = OrderBy.create(objects, sort_by)
    objects = Filter.create(sort, filters)
    return await Paginator(limit=limit, page=page).paginated(
        TextResponseScheme, objects, apply=pagination
    )


@router.post("/", response_model=TextResponseScheme)
@log_action(action=ActionEnum.CREATE.value, model=Text._meta.db_table)
async def create_text_router(
    object: TextCreateScheme,
    user=Depends(login_required),
):
    return await object.create(
        Text,
        serialize=True,
        serializer=TextResponseScheme,
        m2m=[],
    )


@router.get("/{id}", response_model=TextResponseScheme)
@log_action(action=ActionEnum.VIEW.value, model=Text._meta.db_table)
async def get_text_router(
    id: str,
    request: Request,
    user=Depends(login_required),
):
    objects = Text.all()
    return await TextResponseScheme.from_tortoise_orm(
        TextResponseScheme,
        await objects.get(Q(id=id) if str(id).isdigit() else Q(slug=str(id))),
    )


@router.put("/{id}", response_model=TextResponseScheme)
@log_action(action=ActionEnum.UPDATE.value, model=Text._meta.db_table)
async def update_text_router(
    id: int,
    object: TextCreateScheme,
    user=Depends(login_required),
):
    objects = Text.all()
    return await object.update(
        await objects.get(id=id),
        serialize=True,
        serializer=TextResponseScheme,
        m2m=[],
    )


@router.delete("/{id}", response_model=Status)
@log_action(action=ActionEnum.DELETE.value, model=Text._meta.db_table)
async def delete_text_router(id: int):
    objects = Text.all()
    deleted_count = await objects.filter(id=id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Text {id} not found")
    return Status(message=f"Deleted text {id}")
