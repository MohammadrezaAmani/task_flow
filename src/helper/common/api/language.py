from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from tortoise.queryset import Q

from src.app.common import Language, LanguageCreateScheme, LanguageResponseScheme
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

LanguageFilterSchema = create_filter_schema(Language)


@router.get(
    "/", response_model=Paginated[LanguageResponseScheme] | List[LanguageResponseScheme]
)
@log_action(action=ActionEnum.VIEW.value, model=Language._meta.db_table)
async def get_languages_router(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    filters: LanguageFilterSchema = Depends(),  # type: ignore
    user=Depends(login_required),
    sort_by: list[str] = Query([]),
    pagination: bool = Query(True),
):
    objects = Language.all()
    sort = OrderBy.create(objects, sort_by)
    objects = Filter.create(sort, filters)
    return await Paginator(limit=limit, page=page).paginated(
        LanguageResponseScheme, objects, apply=pagination
    )


@router.post("/", response_model=LanguageResponseScheme)
@log_action(action=ActionEnum.CREATE.value, model=Language._meta.db_table)
async def create_language_router(
    object: LanguageCreateScheme,
    user=Depends(login_required),
):
    return await object.create(
        Language,
        serialize=True,
        serializer=LanguageResponseScheme,
        m2m=[],
    )


@router.get("/{id}", response_model=LanguageResponseScheme)
@log_action(action=ActionEnum.VIEW.value, model=Language._meta.db_table)
async def get_language_router(
    id: str,
    request: Request,
    user=Depends(login_required),
):
    objects = Language.all()
    return await LanguageResponseScheme.from_tortoise_orm(
        LanguageResponseScheme,
        await objects.get(Q(id=id) if str(id).isdigit() else Q(slug=str(id))),
    )


@router.put("/{id}", response_model=LanguageResponseScheme)
@log_action(action=ActionEnum.UPDATE.value, model=Language._meta.db_table)
async def update_language_router(
    id: int,
    object: LanguageCreateScheme,
    user=Depends(login_required),
):
    objects = Language.all()
    return await object.update(
        await objects.get(id=id),
        serialize=True,
        serializer=LanguageResponseScheme,
        m2m=[],
    )


@router.delete("/{id}", response_model=Status)
@log_action(action=ActionEnum.DELETE.value, model=Language._meta.db_table)
async def delete_language_router(id: int):
    objects = Language.all()
    deleted_count = await objects.filter(id=id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Language {id} not found")
    return Status(message=f"Deleted language {id}")
