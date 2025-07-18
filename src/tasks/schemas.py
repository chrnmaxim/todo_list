import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.base_schemas import BaseListReadSchema, BaseQuerySchema


# MARK: Query
class TaskQuerySchema(BaseQuerySchema):
    """Схема query-параметров для поиска задач."""

    title: str | None = Field(default=None, description="Заголовок задачи")


# MARK: Tasks
class TaskCreateSchema(BaseModel):
    """Схема для создания задачи."""

    title: str = Field(description="Заголовок задачи")
    description: str | None = Field(default=None, description="Описание задачи")
    to_be_completed_at: datetime | None = Field(
        default=None, description="Дата и время завершения задачи"
    )


class TaskUpdateSchema(BaseModel):
    """Схема для обновления задачи."""

    title: str = Field(description="Заголовок задачи")
    description: str | None = Field(description="Описание задачи")
    to_be_completed_at: datetime | None = Field(
        description="Дата и время завершения задачи"
    )
    is_completed: bool = Field(description="Статус выполнения задачи")


class TaskReadSchema(TaskUpdateSchema):
    """Схема для отображения задачи."""

    id: uuid.UUID = Field(description="Идентификатор задачи")
    created_at: datetime = Field(description="Дата и время создания задачи")
    updated_at: datetime = Field(description="Дата и время обновления задачи")

    model_config = ConfigDict(from_attributes=True)


class TaskReadListSchema(BaseListReadSchema):
    """Схема для отображения списка задач."""

    tasks: list[TaskReadSchema] = Field(description="Список задач")
