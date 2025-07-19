from datetime import timedelta
from typing import AsyncGenerator

import httpx
import pytest_asyncio
from faker import Faker
from fastapi import APIRouter, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_session
from src.tasks.dao import TaskDAO
from src.tasks.models import TaskModel
from src.tasks.schemas import TaskCreateSchema, TaskUpdateSchema

faker = Faker()


# MARK: TestRouter
class BaseTestRouter:
    """Класс для тестирования эндпоинтов."""

    router: APIRouter

    @pytest_asyncio.fixture(scope="function")
    async def router_client(self, session) -> AsyncGenerator[httpx.AsyncClient, None]:
        """
        `AsyncGenerator` для экземпляра `httpx.AsyncClient`.

        Конфигурирует `httpx.ASGITransport` для перенаправления всех запросов
        напрямую в API с использованием протокола ASGI.
        """

        app = FastAPI()
        app.include_router(self.router)
        app.dependency_overrides[get_session] = lambda: session

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as async_client:
            yield async_client


# MARK: Task
@pytest_asyncio.fixture
async def task_data_without_completion() -> TaskCreateSchema:
    """Данные для создания задачи без заданного параметра `time_to_complete`."""

    return TaskCreateSchema(
        title="Обычная задача",
        description=faker.sentence(nb_words=10),
        time_to_complete=None,
    )


@pytest_asyncio.fixture
async def task_db_not_completed(
    task_data_without_completion: TaskCreateSchema, session: AsyncSession
) -> TaskModel:
    """
    Создать незавершенную задачу в БД.

    Для задачи установлено время создания в прошлом
    для проверки корректности сортировки.
    """

    task_db = await TaskDAO.add(session=session, obj_in=task_data_without_completion)
    task_db.created_at = task_db.created_at - timedelta(seconds=10)
    await session.commit()
    return task_db


@pytest_asyncio.fixture
async def task_data_with_completion() -> TaskCreateSchema:
    """Данные для создания задачи с указанным параметром `time_to_complete`."""

    return TaskCreateSchema(
        title="Отложенная задача",
        description=faker.sentence(nb_words=10),
        time_to_complete=10,
    )


@pytest_asyncio.fixture
async def task_db_completed(
    task_data_with_completion: TaskCreateSchema, session: AsyncSession
) -> TaskModel:
    """Создать завершенную задачу в БД."""

    task_db = await TaskDAO.add(session=session, obj_in=task_data_with_completion)
    task_db.is_completed = True
    await session.commit()
    return task_db


@pytest_asyncio.fixture
async def task_data_update() -> TaskUpdateSchema:
    """Данные для обновления задачи."""

    return TaskUpdateSchema(
        title=faker.sentence(nb_words=3),
        description=faker.sentence(nb_words=10),
        is_completed=True,
    )
