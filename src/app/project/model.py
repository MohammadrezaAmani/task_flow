from tortoise import fields

from src.base import BaseModel


class Project(BaseModel):
    name = fields.CharField(max_length=256)
    description = fields.TextField(null=True)
    owner = fields.ForeignKeyField("models.User", related_name="owned_project")
    user = fields.ManyToManyField("models.Access", related_name="project")

    def __repr__(self):
        return self.__str__()

    class Meta:
        table = "project"


class BaseData(BaseModel):
    key = fields.TextField()
    value = fields.TextField()
    category = fields.CharField(max_length=256, null=True)

    def __repr__(self):
        return self.__str__()

    class Meta:
        table = "base_data"


class Board(BaseModel):
    name = fields.CharField(max_length=256)
    project = fields.ForeignKeyField("models.Project", related_name="board")
    color = fields.ForeignKeyField("models.BaseData", null=True)

    def __repr__(self):
        return self.__str__()

    class Meta:
        table = "board"


class Column(BaseModel):
    name = fields.CharField(max_length=256)
    board = fields.ForeignKeyField("models.Board", related_name="column")
    position = fields.FloatField(defult=1000.0)
    color = fields.ForeignKeyField("models.BaseData", null=True)

    def __repr__(self):
        return self.__str__()

    class Meta:
        table = "column"


class CheckList(BaseModel):
    name = fields.CharField(max_length=256)
    description = fields.TextField(null=True)
    user = fields.ForeignKeyField("models.User")
    is_done = fields.BooleanField(default=False)

    def __repr__(self):
        return self.__str__()

    class Meta:
        table = "check_list"


class Task(BaseModel):
    name = fields.CharField(max_length=256)
    board = fields.ForeignKeyField("models.Board", related_name="task")
    position = fields.FloatField(defult=1000.0)
    start_date = fields.DatetimeField(null=True)
    end_date = fields.DatetimeField(null=True)
    description = fields.TextField(null=True)
    is_show_on_card = fields.BooleanField(default=False)
    color = fields.ForeignKeyField(
        "models.BaseData",
        null=True,
        related_name="color",
    )
    progress = fields.ForeignKeyField(
        "models.BaseData",
        null=True,
        related_name="progress",
    )
    priority = fields.ForeignKeyField(
        "models.BaseData",
        null=True,
        related_name="priority",
    )

    checklist = fields.ManyToManyField("models.CheckList", related_name="task")
    comment = fields.ManyToManyField("models.Comment", related_name="task")

    def __repr__(self):
        return self.__str__()

    class Meta:
        table = "task"
