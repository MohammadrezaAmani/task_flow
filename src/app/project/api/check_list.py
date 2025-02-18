from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from tortoise.queryset import Q

from src.app.project import CheckList, CheckListCreateScheme, CheckListResponseScheme
from src.helper import (
    ActionEnum,
    Filter,
    OrderBy,
    Paginated,
    Paginator,
    Status,
    create_filter_schema,
    has_access,
    log_action,
    login_required,
)
from src.helper.user.model import User

router = APIRouter()

CheckListFilterSchema = create_filter_schema(CheckList)

MODEL_NAME: str = CheckList._meta.db_table


@router.get(
    "/",
    response_model=Paginated[CheckListResponseScheme] | List[CheckListResponseScheme],
)
@log_action(action=ActionEnum.VIEW_ALL.value, model=MODEL_NAME)
@has_access(action=ActionEnum.VIEW_ALL.value, to=MODEL_NAME)
async def get_check_lists_router(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    filters: CheckListFilterSchema = Depends(),  # type: ignore
    user: User = Depends(login_required),
    sort_by: list[str] = Query([]),
    pagination: bool = Query(True),
):
    objects = CheckList.all()
    sort = OrderBy.create(objects, sort_by)
    objects = Filter.create(sort, filters)
    return await Paginator(limit=limit, page=page).paginated(
        CheckListResponseScheme, objects, apply=pagination
    )


@router.post("/", response_model=CheckListResponseScheme)
@log_action(action=ActionEnum.CREATE.value, model=MODEL_NAME)
@has_access(action=ActionEnum.CREATE.value, to=MODEL_NAME)
async def create_check_list_router(
    object: CheckListCreateScheme,
    user: User = Depends(login_required),
):
    return await object.create(
        CheckList,
        serialize=True,
        serializer=CheckListResponseScheme,
        m2m=[],
    )


@router.get("/{id}", response_model=CheckListResponseScheme)
@log_action(action=ActionEnum.VIEW.value, model=MODEL_NAME)
@has_access(action=ActionEnum.VIEW.value, to=MODEL_NAME)
async def get_check_list_router(
    id: str,
    request: Request,
    user: User = Depends(login_required),
):
    objects = CheckList.all()
    return await CheckListResponseScheme.from_tortoise_orm(
        CheckListResponseScheme,
        await objects.get(Q(id=id) if str(id).isdigit() else Q(slug=str(id))),
    )


@router.put("/{id}", response_model=CheckListResponseScheme)
@log_action(action=ActionEnum.UPDATE.value, model=MODEL_NAME)
@has_access(action=ActionEnum.UPDATE.value, to=MODEL_NAME)
async def update_check_list_router(
    id: int,
    object: CheckListCreateScheme,
    user: User = Depends(login_required),
):
    objects = CheckList.all()
    return await object.update(
        await objects.get(id=id),
        serialize=True,
        serializer=CheckListResponseScheme,
        m2m=[],
    )


@router.delete("/{id}", response_model=Status)
@log_action(action=ActionEnum.DELETE.value, model=MODEL_NAME)
@has_access(action=ActionEnum.DELETE.value, to=MODEL_NAME)
async def delete_check_list_router(id: int, user: User = Depends(login_required)):
    objects = CheckList.filter().all()
    deleted_count = await objects.filter(id=id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"CheckList {id} not found")
    return Status(message=f"Deleted check_list {id}")
