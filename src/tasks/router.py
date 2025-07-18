import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_session
from src.tasks.schemas import (
    TaskCreateSchema,
    TaskQuerySchema,
    TaskReadListSchema,
    TaskReadSchema,
    TaskUpdateSchema,
)
from src.tasks.service import TaskService

__all__ = ["tasks_router"]

tasks_router = APIRouter(prefix="/tasks", tags=["Задачи"])


# MARK: Get
@tasks_router.get(
    "",
    summary="Получить список задач",
    status_code=status.HTTP_200_OK,
    response_model=None,
    responses={status.HTTP_200_OK: {"model": TaskReadListSchema}},
)
async def get_tasks_route(
    query: TaskQuerySchema = Query(),
    session: AsyncSession = Depends(get_session),
) -> TaskReadListSchema:
    """
    Получить список задач с фильтрацией по переданным
    query-параметрам и с учетом пагинации.

    По умолчанию сортировка выполняется по дате создания задачи.
    """

    return await TaskService.get_tasks(query=query, session=session)


# MARK: Post
@tasks_router.post(
    "",
    summary="Создать задачу",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
    responses={status.HTTP_201_CREATED: {"model": TaskReadSchema}},
)
async def create_task_route(
    task_data: TaskCreateSchema,
    session: AsyncSession = Depends(get_session),
) -> TaskReadSchema:
    """Создать новую задачу."""

    return await TaskService.create_task(task_data=task_data, session=session)


# MARK: Put
@tasks_router.put(
    "",
    summary="Обновить задачу по id",
    status_code=status.HTTP_200_OK,
    response_model=None,
    responses={status.HTTP_200_OK: {"model": TaskReadSchema}},
)
async def update_task_route(
    task_data: TaskUpdateSchema,
    task_id: uuid.UUID = Query(description="Идентификатор задачи"),
    session: AsyncSession = Depends(get_session),
) -> TaskReadSchema:
    """
    Обновить задачу по id.

    Raises:

        TaskNotFound: Задача не найдена `HTTP_404_NOT_FOUND`.
    """

    return await TaskService.update_task(
        task_data=task_data, task_id=task_id, session=session
    )


# MARK: Delete
@tasks_router.delete(
    "",
    summary="Удалить задачу по id",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_task_route(
    task_id: uuid.UUID = Query(description="Идентификатор задачи"),
    session: AsyncSession = Depends(get_session),
) -> None:
    """
    Удалить задачу по id.

    Raises:

        TaskNotFound: Задача не найдена `HTTP_404_NOT_FOUND`.
    """

    return await TaskService.delete_task(task_id=task_id, session=session)
