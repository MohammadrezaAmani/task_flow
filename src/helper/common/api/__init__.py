from fastapi import APIRouter

from src.app.common.api.action import router as action_router
from src.app.common.api.category import router as category_router
from src.app.common.api.comment import router as comment_router
from src.app.common.api.language import router as language_router
from src.app.common.api.react import router as react_router
from src.app.common.api.tag import router as tag_router
from src.app.common.api.text import router as text_router
from src.helper import add_patterns

api_patterns = [
    (language_router, "/language", ["Language"], {}),
    (text_router, "/text", ["Text"], {}),
    (tag_router, "/tag", ["Tag"], {}),
    (action_router, "/action", ["Action"], {}),
    (react_router, "/react", ["React"], {}),
    (comment_router, "/comment", ["Comment"], {}),
    (category_router, "/category", ["Category"], {}),
]

router = add_patterns(APIRouter(), api_patterns)
