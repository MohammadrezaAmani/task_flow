from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from tortoise.queryset import Q

from src.app.project import Board, BoardCreateScheme, BoardResponseScheme
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

BoardFilterSchema = create_filter_schema(Board)

MODEL_NAME: str = Board._meta.db_table


@router.get(
    "/", response_model=Paginated[BoardResponseScheme] | List[BoardResponseScheme]
)
@log_action(action=ActionEnum.VIEW_ALL.value, model=MODEL_NAME)
@has_access(action=ActionEnum.VIEW_ALL.value, to=MODEL_NAME)
async def get_boards_router(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    filters: BoardFilterSchema = Depends(),  # type: ignore
    user: User = Depends(login_required),
    sort_by: list[str] = Query([]),
    pagination: bool = Query(True),
):
    objects = Board.all()
    sort = OrderBy.create(objects, sort_by)
    objects = Filter.create(sort, filters)
    return await Paginator(limit=limit, page=page).paginated(
        BoardResponseScheme, objects, apply=pagination
    )


@router.post("/", response_model=BoardResponseScheme)
@log_action(action=ActionEnum.CREATE.value, model=MODEL_NAME)
@has_access(action=ActionEnum.CREATE.value, to=MODEL_NAME)
async def create_board_router(
    object: BoardCreateScheme,
    user: User = Depends(login_required),
):
    return await object.create(
        Board,
        serialize=True,
        serializer=BoardResponseScheme,
        m2m=[],
    )


@router.get("/{id}", response_model=BoardResponseScheme)
@log_action(action=ActionEnum.VIEW.value, model=MODEL_NAME)
@has_access(action=ActionEnum.VIEW.value, to=MODEL_NAME)
async def get_board_router(
    id: str,
    request: Request,
    user: User = Depends(login_required),
):
    objects = Board.all()
    return await BoardResponseScheme.from_tortoise_orm(
        BoardResponseScheme,
        await objects.get(Q(id=id) if str(id).isdigit() else Q(slug=str(id))),
    )


@router.put("/{id}", response_model=BoardResponseScheme)
@log_action(action=ActionEnum.UPDATE.value, model=MODEL_NAME)
@has_access(action=ActionEnum.UPDATE.value, to=MODEL_NAME)
async def update_board_router(
    id: int,
    object: BoardCreateScheme,
    user: User = Depends(login_required),
):
    objects = Board.all()
    return await object.update(
        await objects.get(id=id),
        serialize=True,
        serializer=BoardResponseScheme,
        m2m=[],
    )


@router.delete("/{id}", response_model=Status)
@log_action(action=ActionEnum.DELETE.value, model=MODEL_NAME)
@has_access(action=ActionEnum.DELETE.value, to=MODEL_NAME)
async def delete_board_router(id: int, user: User = Depends(login_required)):
    objects = Board.filter().all()
    deleted_count = await objects.filter(id=id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Board {id} not found")
    return Status(message=f"Deleted board {id}")
