from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from tortoise.queryset import Q

from src.app.common import Action, ActionCreateScheme, ActionResponseScheme
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

ActionFilterSchema = create_filter_schema(Action)


@router.get(
    "/", response_model=Paginated[ActionResponseScheme] | List[ActionResponseScheme]
)
@log_action(action=ActionEnum.VIEW.value, model=Action._meta.db_table)
async def get_actions_router(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    filters: ActionFilterSchema = Depends(),  # type: ignore
    user=Depends(login_required),
    sort_by: list[str] = Query([]),
    pagination: bool = Query(True),
):
    objects = Action.all()
    sort = OrderBy.create(objects, sort_by)
    objects = Filter.create(sort, filters)
    return await Paginator(limit=limit, page=page).paginated(
        ActionResponseScheme, objects, apply=pagination
    )


@router.post("/", response_model=ActionResponseScheme)
@log_action(action=ActionEnum.CREATE.value, model=Action._meta.db_table)
async def create_action_router(
    object: ActionCreateScheme,
    user=Depends(login_required),
):
    return await object.create(
        Action,
        serialize=True,
        serializer=ActionResponseScheme,
        m2m=[],
    )


@router.get("/{id}", response_model=ActionResponseScheme)
@log_action(action=ActionEnum.VIEW.value, model=Action._meta.db_table)
async def get_action_router(
    id: str,
    request: Request,
    user=Depends(login_required),
):
    objects = Action.all()
    return await ActionResponseScheme.from_tortoise_orm(
        ActionResponseScheme,
        await objects.get(Q(id=id) if str(id).isdigit() else Q(slug=str(id))),
    )


@router.put("/{id}", response_model=ActionResponseScheme)
@log_action(action=ActionEnum.UPDATE.value, model=Action._meta.db_table)
async def update_action_router(
    id: int,
    object: ActionCreateScheme,
    user=Depends(login_required),
):
    objects = Action.all()
    return await object.update(
        await objects.get(id=id),
        serialize=True,
        serializer=ActionResponseScheme,
        m2m=[],
    )


@router.delete("/{id}", response_model=Status)
@log_action(action=ActionEnum.DELETE.value, model=Action._meta.db_table)
async def delete_action_router(id: int):
    objects = Action.all()
    deleted_count = await objects.filter(id=id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Action {id} not found")
    return Status(message=f"Deleted action {id}")
