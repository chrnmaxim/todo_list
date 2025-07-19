import asyncio
import uuid

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src import exceptions
from src.tasks.dao import TaskDAO
from src.tasks.models import TaskModel
from src.tasks.schemas import (
    TaskCreateSchema,
    TaskQuerySchema,
    TaskReadListSchema,
    TaskReadSchema,
    TaskUpdateSchema,
)


class TaskService:
    """
    Класс для работы с задачами.

    Позволяет выполнять CRUD операции.
    """

    # MARK: BackgroundTasks
    @classmethod
    async def _update_task_status_in_background(
        cls,
        task_id: uuid.UUID,
        time_to_complete: int,
        session: AsyncSession,
    ) -> None:
        """Фоновая задача для обновления статуса задачи по истечении времени."""

        await asyncio.sleep(time_to_complete)
        await TaskDAO.partial_update(
            TaskModel.id == task_id, obj_in={"is_completed": True}, session=session
        )
        await session.commit()

    # MARK: Create
    @classmethod
    async def create_task(
        cls,
        background_tasks: BackgroundTasks,
        task_data: TaskCreateSchema,
        session: AsyncSession,
    ) -> TaskReadSchema:
        """
        Создать новую задачу.

        Если задан параметр `task_data.to_be_completed_at`, то запустится
        фоновая задача FastAPI, которая изменит статус задачи
        на `is_completed=True` по истечении указанного времени.
        """

        created_task_id = await TaskDAO.add_returning_id(
            session=session, obj_in=task_data
        )
        await session.commit()

        if task_data.time_to_complete is not None:
            background_tasks.add_task(
                func=cls._update_task_status_in_background,
                task_id=created_task_id,
                time_to_complete=task_data.time_to_complete,
                session=session,
            )

        return TaskReadSchema(
            title=task_data.title,
            description=task_data.description,
            is_completed=False,
            id=created_task_id,
        )

    # MARK: Read
    @classmethod
    async def get_tasks(
        cls, query: TaskQuerySchema, session: AsyncSession
    ) -> TaskReadListSchema:
        """
        Получить список задач с фильтрацией по переданным
        query-параметрам и с учетом пагинации.

        По умолчанию сортировка выполняется по дате создания задачи.
        """

        where = []
        if query.title is not None:
            where.append(TaskModel.title.ilike(f"%{query.title}%"))

        count = await TaskDAO.count(*where, session=session)
        if count:
            task_mappings = await TaskDAO.get_tasks_data(
                *where,
                offset=query.offset,
                limit=query.limit,
                asc=query.asc,
                session=session,
            )
            tasks = [TaskReadSchema.model_validate(task) for task in task_mappings]

        else:
            tasks = []

        return TaskReadListSchema(count=count, tasks=tasks)

    # MARK: Update
    @classmethod
    async def update_task(
        cls, task_data: TaskUpdateSchema, task_id: uuid.UUID, session: AsyncSession
    ) -> TaskReadSchema:
        """
        Обновить задачу по id.

        Raises:
            TaskNotFound: Задача не найдена `HTTP_404_NOT_FOUND`.
        """

        updated_task_data = await TaskDAO.update_task_full_data(
            task_data=task_data, task_id=task_id, session=session
        )
        if updated_task_data is None:
            raise exceptions.TaskNotFound

        await session.commit()

        return TaskReadSchema(
            title=task_data.title,
            description=task_data.description,
            is_completed=task_data.is_completed,
            id=task_id,
            completion=updated_task_data["completion"],
        )

    # MARK: Delete
    @classmethod
    async def delete_task(cls, task_id: uuid.UUID, session: AsyncSession) -> None:
        """
        Обновить задачу по id.

        Raises:
            TaskNotFound: Задача не найдена `HTTP_404_NOT_FOUND`.
        """

        deleted_task_id = await TaskDAO.delete_returning_id(
            TaskModel.id == task_id, session=session
        )
        if deleted_task_id is None:
            raise exceptions.TaskNotFound

        await session.commit()
