import uuid

from sqlalchemy import Label, case, func, select, text, update
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao import BaseDAO
from src.tasks.models import TaskModel
from src.tasks.schemas import TaskCreateSchema, TaskUpdateSchema


class TaskDAO(BaseDAO[TaskModel, TaskCreateSchema, TaskUpdateSchema]):
    """DAO для работы с задачами."""

    model = TaskModel

    @classmethod
    def _get_task_completion_exp(cls) -> Label:
        """Получить выражение для вычисления прогресса выполнения задачи."""

        interval_expr = cls.model.time_to_complete * text("interval '1 second'")
        task_end_time = cls.model.created_at + interval_expr
        task_time_left = task_end_time - func.now()
        zero_interval = text("interval '0'")

        completion_expr = func.floor(
            (
                1
                - func.extract("epoch", task_time_left)
                / func.extract("epoch", interval_expr)
            )
            * 100
        )

        return case(
            (cls.model.is_completed.is_(True), 100),
            (
                cls.model.time_to_complete.is_not(None),
                case(
                    (task_time_left < zero_interval, 100),
                    else_=completion_expr,
                ),
            ),
            else_=0,
        ).label("completion")

    @classmethod
    async def get_tasks_data(
        cls,
        *where,
        offset: int | None,
        limit: int | None,
        asc: bool,
        session: AsyncSession,
    ) -> list[RowMapping]:
        """
        Получить основные данные задач с учетом фильтрации и пагинации.

        Returns:
            list[RowMapping]: список `RowMapping` с основными данными задач.
        """

        stmt = (
            select(
                cls.model.id,
                cls.model.title,
                cls.model.description,
                cls.model.is_completed,
                cls._get_task_completion_exp(),
            )
            .where(*where)
            .offset(offset)
            .limit(limit)
            .order_by(
                cls.model.created_at.asc() if asc else cls.model.created_at.desc()
            )
        )

        result = await session.execute(stmt)
        return result.mappings().all()

    @classmethod
    async def update_task_full_data(
        cls,
        task_data: TaskUpdateSchema,
        task_id: uuid.UUID,
        session: AsyncSession,
    ) -> RowMapping | None:
        """
        Обновить задачу по id и вернуть обновленные данные.

        Returns:
            RowMapping:
                `RowMapping` из `id` задачи и прогресса выполнения `completion`
                или `None`, если задача не найдена.
        """

        stmt = (
            update(cls.model)
            .where(cls.model.id == task_id)
            .values(**task_data.model_dump())
            .returning(cls.model.id, cls._get_task_completion_exp())
        )
        result = await session.execute(stmt)
        return result.mappings().one_or_none()
