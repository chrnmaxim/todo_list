import uuid

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
    time_to_complete: int | None = Field(
        default=None, description="Время до завершения задачи в секундах", ge=10, le=300
    )


class TaskUpdateSchema(BaseModel):
    """Схема для обновления задачи."""

    title: str = Field(description="Заголовок задачи")
    description: str | None = Field(description="Описание задачи")
    is_completed: bool = Field(description="Статус выполнения задачи")


class TaskReadSchema(TaskUpdateSchema):
    """Схема для отображения задачи."""

    id: uuid.UUID = Field(description="Идентификатор задачи")
    completion: int = Field(
        default=0,
        description="Прогресс выполнения задачи, %",
    )

    model_config = ConfigDict(from_attributes=True)


class TaskReadListSchema(BaseListReadSchema):
    """Схема для отображения списка задач."""

    tasks: list[TaskReadSchema] = Field(description="Список задач")
