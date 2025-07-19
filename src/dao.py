import uuid
from typing import Any, Generic, Literal, Tuple, TypeVar, overload

from pydantic import BaseModel
from sqlalchemy import Select, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseDAO(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Основной класс интерфейсов для операций с моделям БД.

    Атрибуты класса:
        model (Type[ModelType]): модель SQLAlchemy.
    """

    model = Base

    # MARK: Create
    @classmethod
    async def add_returning_id(
        cls,
        session: AsyncSession,
        obj_in: CreateSchemaType | dict[str, Any],
    ) -> uuid.UUID:
        """
        Добавить запись в текущую сессию и вернуть `id` созданной записи.

        Если `obj_in` является моделью Pydantic, из него удаляются не заданные явно поля.

        Args:
            session(AsyncSession): асинхронная сессия SQLAlchemy.
            obj_in(CreateSchemaType | dict[str, Any]): Pydantic-схема или словарь данных
                для обновления.

        Returns:
            uuid.UUID: `id` созданного экземпляра модели.
        """

        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)

        stmt = insert(cls.model).values(**create_data).returning(cls.model.id)
        result = await session.execute(stmt)
        return result.scalar_one()

    # MARK: Read
    @classmethod
    async def find_all_sorted(
        cls,
        *where,
        session: AsyncSession,
        order_by,
        offset: int | None,
        limit: int | None,
        asc: bool,
    ) -> list[ModelType]:
        """
        Получить все записи с фильтрацией по переданным
        query-параметрам и с учетом пагинации.

        Returns:
            list[ModelType]: модели, соответствующие параметрам поиска.
        """

        stmt = (
            select(cls.model)
            .where(*where)
            .offset(offset)
            .limit(limit)
            .order_by(order_by.asc() if asc else order_by.desc())
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    # MARK: Update
    @classmethod
    @overload
    async def partial_update(
        cls,
        *where,
        session: AsyncSession,
        obj_in: UpdateSchemaType | dict[str, Any],
        returning: Literal[True],
    ) -> ModelType: ...

    @classmethod
    @overload
    async def partial_update(
        cls,
        *where,
        session: AsyncSession,
        obj_in: UpdateSchemaType | dict[str, Any],
        returning: Literal[False] = False,
    ) -> ModelType: ...

    @classmethod
    async def partial_update(
        cls,
        *where,
        session: AsyncSession,
        obj_in: UpdateSchemaType | dict[str, Any],
        returning: bool = True,
    ) -> ModelType | None:
        """
        Обновить запись частично в текущей сессии. Применимо для `PATCH`-запросов.

        Если `obj_in` является моделью Pydantic, из него удаляются не заданные явно поля.

        Returns:
            ModelType|None:
                обновленный экземпляр модели или `None`, если запись не найдена
                или указан параметр `returning=False`.
        """

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        stmt = update(cls.model).where(*where).values(**update_data)
        if returning:
            stmt = stmt.returning(cls.model)
            return await session.scalar(stmt)
        else:
            await session.execute(stmt)

    # MARK: Delete
    @classmethod
    async def delete_returning_id(
        cls,
        *where,
        session: AsyncSession,
    ) -> uuid.UUID | None:
        """
        Удалить запись, соответствующую критериям.

        Returns:
            uuid.UUID|None: `id` удаленного экземпляра модели или `None`, если запись не найдена.
        """

        stmt = delete(cls.model).where(*where).returning(cls.model.id)
        return await session.scalar(stmt)

    # MARK: Count
    @classmethod
    async def count(
        cls,
        *where,
        session: AsyncSession,
    ) -> int:
        """
        Посчитать строки в БД, соответствующий критериям.

        Returns:
            rows_count: количество найденных строк или 0 если совпадений не найдено.
        """

        stmt = select(func.count()).select_from(cls.model).where(*where)
        return await session.scalar(stmt) or 0

    @classmethod
    async def count_from_stmt(
        cls,
        session: AsyncSession,
        count_stmt: Select[Tuple[int]],
    ) -> int:
        """
        Получить общее количество сущностей в БД, используя выражение
        для подсчета строк в БД, предварительно составленное с учетом фильтрации.

        Returns:
            total_count: общее количество сущностей.
        """

        return await session.scalar(count_stmt) or 0
