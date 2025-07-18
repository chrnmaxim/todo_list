import uuid

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

    # MARK: Create
    @classmethod
    async def create_task(
        cls, task_data: TaskCreateSchema, session: AsyncSession
    ) -> TaskReadSchema:
        """Создать новую задачу."""

        created_task = await TaskDAO.add(session=session, obj_in=task_data)
        await session.commit()

        return TaskReadSchema.model_validate(created_task)

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
            tasks = await TaskDAO.find_all_sorted(
                *where,
                session=session,
                order_by=TaskModel.created_at,
                offset=query.offset,
                limit=query.limit,
                asc=query.asc,
            )
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

        updated_task = await TaskDAO.full_update(
            TaskModel.id == task_id, session=session, obj_in=task_data
        )
        if updated_task is None:
            raise exceptions.TaskNotFound
        await session.commit()

        return TaskReadSchema.model_validate(updated_task)

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
