from fastapi import APIRouter

from src.app.project.api.base_data import router as base_data_router
from src.app.project.api.board import router as board_router
from src.app.project.api.check_list import router as check_list_router
from src.app.project.api.column import router as column_router
from src.app.project.api.project import router as project_router
from src.app.project.api.task import router as task_router
from src.helper import add_patterns

api_patterns = [
    (project_router, "/project", ["Project"], {}),
    (base_data_router, "/base_data", ["Base Data"], {}),
    (board_router, "/board", ["Board"], {}),
    (check_list_router, "/check_list", ["Check List"], {}),
    (column_router, "/column", ["Column"], {}),
    (task_router, "/task", ["Task"], {}),
]

router = add_patterns(APIRouter(), api_patterns)
