from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from tortoise.queryset import Q

from src.app.common import Comment, CommentCreateScheme, CommentResponseScheme
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

CommentFilterSchema = create_filter_schema(Comment)


@router.get(
    "/", response_model=Paginated[CommentResponseScheme] | List[CommentResponseScheme]
)
@log_action(action=ActionEnum.VIEW.value, model=Comment._meta.db_table)
async def get_comments_router(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    filters: CommentFilterSchema = Depends(),  # type: ignore
    user=Depends(login_required),
    sort_by: list[str] = Query([]),
    pagination: bool = Query(True),
):
    objects = Comment.all()
    sort = OrderBy.create(objects, sort_by)
    objects = Filter.create(sort, filters)
    return await Paginator(limit=limit, page=page).paginated(
        CommentResponseScheme, objects, apply=pagination
    )


@router.post("/", response_model=CommentResponseScheme)
@log_action(action=ActionEnum.CREATE.value, model=Comment._meta.db_table)
async def create_comment_router(
    object: CommentCreateScheme,
    user=Depends(login_required),
):
    return await object.create(
        Comment,
        serialize=True,
        serializer=CommentResponseScheme,
        m2m=[],
    )


@router.get("/{id}", response_model=CommentResponseScheme)
@log_action(action=ActionEnum.VIEW.value, model=Comment._meta.db_table)
async def get_comment_router(
    id: str,
    request: Request,
    user=Depends(login_required),
):
    objects = Comment.all()
    return await CommentResponseScheme.from_tortoise_orm(
        CommentResponseScheme,
        await objects.get(Q(id=id) if str(id).isdigit() else Q(slug=str(id))),
    )


@router.put("/{id}", response_model=CommentResponseScheme)
@log_action(action=ActionEnum.UPDATE.value, model=Comment._meta.db_table)
async def update_comment_router(
    id: int,
    object: CommentCreateScheme,
    user=Depends(login_required),
):
    objects = Comment.all()
    return await object.update(
        await objects.get(id=id),
        serialize=True,
        serializer=CommentResponseScheme,
        m2m=[],
    )


@router.delete("/{id}", response_model=Status)
@log_action(action=ActionEnum.DELETE.value, model=Comment._meta.db_table)
async def delete_comment_router(id: int):
    objects = Comment.all()
    deleted_count = await objects.filter(id=id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Comment {id} not found")
    return Status(message=f"Deleted comment {id}")
