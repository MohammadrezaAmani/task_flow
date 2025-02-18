from datetime import datetime

from src.base.scheme import BaseCreateScheme, BaseResponseScheme


class ProjectCreateScheme(BaseCreateScheme):
    name: str | None = None
    description: str | None = None
    owner_id: int | None = None
    user: list[int] | None = None


class ProjectResponseScheme(ProjectCreateScheme, BaseResponseScheme): ...


class BaseDataCreateScheme(BaseCreateScheme):
    key: str | None = None
    value: str | None = None
    category: str | None = None


class BaseDataResponseScheme(BaseDataCreateScheme, BaseResponseScheme): ...


class BoardCreateScheme(BaseCreateScheme):
    name: str | None = None
    project_id: int | None = None
    color_id: int | None = None


class BoardResponseScheme(BoardCreateScheme, BaseResponseScheme): ...


class CheckListCreateScheme(BaseCreateScheme):
    name: str | None = None
    description: str | None = None
    user_id: str | None = None
    is_done: bool = False


class CheckListResponseScheme(CheckListCreateScheme, BaseResponseScheme): ...


class ColumnCreateScheme(BaseCreateScheme):
    name: str | None = None
    board_id: int | None = None
    position: str | None = None
    color_id: int | None = None


class ColumnResponseScheme(ColumnCreateScheme, BaseResponseScheme): ...


class TaskCreateScheme(BaseCreateScheme):
    name: str | None = None
    board_id: str | None = None
    position: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    description: str | None = None
    is_show_on_card: bool | None = None
    color_id: int | None = None
    progress_id: int | None = None
    priority_id: int | None = None
    checklist: list[int] | None = None
    comment: list[int] | None = None


class TaskResponseScheme(TaskCreateScheme, BaseResponseScheme): ...
