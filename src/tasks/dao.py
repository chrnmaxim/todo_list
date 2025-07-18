from src.dao import BaseDAO
from src.tasks.models import TaskModel
from src.tasks.schemas import TaskCreateSchema, TaskUpdateSchema


class TaskDAO(BaseDAO[TaskModel, TaskCreateSchema, TaskUpdateSchema]):
    """DAO для работы с задачами."""

    model = TaskModel
