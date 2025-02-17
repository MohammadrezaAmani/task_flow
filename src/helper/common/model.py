
from src.base import BaseModel


class Language(BaseModel):
    def __repr__(self):
        return self.__str__()

    class Meta:
        table = "language"


class Text(BaseModel):
    def __repr__(self):
        return self.__str__()

    class Meta:
        table = "text"


class Tag(BaseModel):
    def __repr__(self):
        return self.__str__()

    class Meta:
        table = "tag"


class Action(BaseModel):
    def __repr__(self):
        return self.__str__()

    class Meta:
        table = "action"


class React(BaseModel):
    def __repr__(self):
        return self.__str__()

    class Meta:
        table = "react"


class Comment(BaseModel):
    def __repr__(self):
        return self.__str__()

    class Meta:
        table = "comment"


class Category(BaseModel):
    def __repr__(self):
        return self.__str__()

    class Meta:
        table = "category"
