from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from tortoise.queryset import Q

from src.app.project import Project, ProjectCreateScheme, ProjectResponseScheme
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

ProjectFilterSchema = create_filter_schema(Project)

MODEL_NAME: str = Project._meta.db_table


@router.get(
    "/", response_model=Paginated[ProjectResponseScheme] | List[ProjectResponseScheme]
)
@log_action(action=ActionEnum.VIEW_ALL.value, model=MODEL_NAME)
@has_access(action=ActionEnum.VIEW_ALL.value, to=MODEL_NAME)
async def get_projects_router(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    filters: ProjectFilterSchema = Depends(),  # type: ignore
    user: User = Depends(login_required),
    sort_by: list[str] = Query([]),
    pagination: bool = Query(True),
):
    objects = Project.all()
    sort = OrderBy.create(objects, sort_by)
    objects = Filter.create(sort, filters)
    return await Paginator(limit=limit, page=page).paginated(
        ProjectResponseScheme, objects, apply=pagination
    )


@router.post("/", response_model=ProjectResponseScheme)
@log_action(action=ActionEnum.CREATE.value, model=MODEL_NAME)
@has_access(action=ActionEnum.CREATE.value, to=MODEL_NAME)
async def create_project_router(
    object: ProjectCreateScheme,
    user: User = Depends(login_required),
):
    return await object.create(
        Project,
        serialize=True,
        serializer=ProjectResponseScheme,
        m2m=[],
    )


@router.get("/{id}", response_model=ProjectResponseScheme)
@log_action(action=ActionEnum.VIEW.value, model=MODEL_NAME)
@has_access(action=ActionEnum.VIEW.value, to=MODEL_NAME)
async def get_project_router(
    id: str,
    request: Request,
    user: User = Depends(login_required),
):
    objects = Project.all()
    return await ProjectResponseScheme.from_tortoise_orm(
        ProjectResponseScheme,
        await objects.get(Q(id=id) if str(id).isdigit() else Q(slug=str(id))),
    )


@router.put("/{id}", response_model=ProjectResponseScheme)
@log_action(action=ActionEnum.UPDATE.value, model=MODEL_NAME)
@has_access(action=ActionEnum.UPDATE.value, to=MODEL_NAME)
async def update_project_router(
    id: int,
    object: ProjectCreateScheme,
    user: User = Depends(login_required),
):
    objects = Project.all()
    return await object.update(
        await objects.get(id=id),
        serialize=True,
        serializer=ProjectResponseScheme,
        m2m=[],
    )


@router.delete("/{id}", response_model=Status)
@log_action(action=ActionEnum.DELETE.value, model=MODEL_NAME)
@has_access(action=ActionEnum.DELETE.value, to=MODEL_NAME)
async def delete_project_router(id: int, user: User = Depends(login_required)):
    objects = Project.filter().all()
    deleted_count = await objects.filter(id=id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Project {id} not found")
    return Status(message=f"Deleted project {id}")
