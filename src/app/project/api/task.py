from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from tortoise.queryset import Q

from src.app.project import Task, TaskCreateScheme, TaskResponseScheme
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

TaskFilterSchema = create_filter_schema(Task)

MODEL_NAME: str = Task._meta.db_table


@router.get(
    "/", response_model=Paginated[TaskResponseScheme] | List[TaskResponseScheme]
)
@log_action(action=ActionEnum.VIEW_ALL.value, model=MODEL_NAME)
@has_access(action=ActionEnum.VIEW_ALL.value, to=MODEL_NAME)
async def get_tasks_router(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    filters: TaskFilterSchema = Depends(),  # type: ignore
    user: User = Depends(login_required),
    sort_by: list[str] = Query([]),
    pagination: bool = Query(True),
):
    objects = Task.all()
    sort = OrderBy.create(objects, sort_by)
    objects = Filter.create(sort, filters)
    return await Paginator(limit=limit, page=page).paginated(
        TaskResponseScheme, objects, apply=pagination
    )


@router.post("/", response_model=TaskResponseScheme)
@log_action(action=ActionEnum.CREATE.value, model=MODEL_NAME)
@has_access(action=ActionEnum.CREATE.value, to=MODEL_NAME)
async def create_task_router(
    object: TaskCreateScheme,
    user: User = Depends(login_required),
):
    return await object.create(
        Task,
        serialize=True,
        serializer=TaskResponseScheme,
        m2m=[],
    )


@router.get("/{id}", response_model=TaskResponseScheme)
@log_action(action=ActionEnum.VIEW.value, model=MODEL_NAME)
@has_access(action=ActionEnum.VIEW.value, to=MODEL_NAME)
async def get_task_router(
    id: str,
    request: Request,
    user: User = Depends(login_required),
):
    objects = Task.all()
    return await TaskResponseScheme.from_tortoise_orm(
        TaskResponseScheme,
        await objects.get(Q(id=id) if str(id).isdigit() else Q(slug=str(id))),
    )


@router.put("/{id}", response_model=TaskResponseScheme)
@log_action(action=ActionEnum.UPDATE.value, model=MODEL_NAME)
@has_access(action=ActionEnum.UPDATE.value, to=MODEL_NAME)
async def update_task_router(
    id: int,
    object: TaskCreateScheme,
    user: User = Depends(login_required),
):
    objects = Task.all()
    return await object.update(
        await objects.get(id=id),
        serialize=True,
        serializer=TaskResponseScheme,
        m2m=[],
    )


@router.delete("/{id}", response_model=Status)
@log_action(action=ActionEnum.DELETE.value, model=MODEL_NAME)
@has_access(action=ActionEnum.DELETE.value, to=MODEL_NAME)
async def delete_task_router(id: int, user: User = Depends(login_required)):
    objects = Task.filter().all()
    deleted_count = await objects.filter(id=id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    return Status(message=f"Deleted task {id}")
