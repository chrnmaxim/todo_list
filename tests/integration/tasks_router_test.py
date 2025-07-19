import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.tasks.dao import TaskDAO
from src.tasks.models import TaskModel
from src.tasks.router import tasks_router
from src.tasks.schemas import (
    TaskCreateSchema,
    TaskReadListSchema,
    TaskReadSchema,
    TaskUpdateSchema,
)
from tests.integration.conftest import BaseTestRouter


class TestTasksRouter(BaseTestRouter):
    """
    Класс для тестирования эндпоинтов роутера
    src.tasks.router.tasks_router.
    """

    router = tasks_router

    # MARK: Get
    async def test_get_tasks_no_query(
        self,
        router_client: httpx.AsyncClient,
        task_db_not_completed: TaskModel,
        task_db_completed: TaskModel,
    ):
        """
        Возможно получить задачи из БД без использования query параметров.

        * `task_db_not_completed` - незавершенная 'Обычная задача' с временным создания в прошлом;
        * `task_db_completed` - завершенная 'Отложенная задача' с текущим временем создания.
        """

        response = await router_client.get(url="/tasks")
        assert response.status_code == status.HTTP_200_OK

        tasks_data = TaskReadListSchema(**response.json())
        assert tasks_data.count == 2
        assert len(tasks_data.tasks) == 2

        assert tasks_data.tasks[0].id == task_db_not_completed.id
        assert tasks_data.tasks[0].title == task_db_not_completed.title
        assert tasks_data.tasks[0].description == task_db_not_completed.description
        assert tasks_data.tasks[0].is_completed is False
        assert tasks_data.tasks[0].completion == 0

        assert tasks_data.tasks[1].id == task_db_completed.id
        assert tasks_data.tasks[1].title == task_db_completed.title
        assert tasks_data.tasks[1].description == task_db_completed.description
        assert tasks_data.tasks[1].is_completed is True
        assert tasks_data.tasks[1].completion == 100

    async def test_get_tasks_query(
        self,
        router_client: httpx.AsyncClient,
        task_db_not_completed: TaskModel,
        task_db_completed: TaskModel,
    ):
        """
        Возможно получить задачи из БД без использования query параметров.

        * `task_db_not_completed` - незавершенная 'Обычная задача' с временным создания в прошлом;
        * `task_db_completed` - завершенная 'Отложенная задача' с текущим временем создания,
        передаётся для проверки фильтрации по заголовку задачи.
        """

        response = await router_client.get(url="/tasks", params={"title": "обычная"})
        assert response.status_code == status.HTTP_200_OK

        tasks_data = TaskReadListSchema(**response.json())
        assert tasks_data.count == 1
        assert len(tasks_data.tasks) == 1

        assert tasks_data.tasks[0].id == task_db_not_completed.id
        assert tasks_data.tasks[0].title == task_db_not_completed.title
        assert tasks_data.tasks[0].description == task_db_not_completed.description
        assert tasks_data.tasks[0].is_completed is False
        assert tasks_data.tasks[0].completion == 0

    # MARK: Post
    async def test_create_task_without_completion(
        self,
        session: AsyncSession,
        router_client: httpx.AsyncClient,
        task_data_without_completion: TaskCreateSchema,
        mocker,
    ):
        """Возможно создать задачу без указания параметра `time_to_complete`."""

        background_task = mocker.patch(
            "src.tasks.service.TaskService._update_task_status_in_background",
            return_value=None,
        )

        response = await router_client.post(
            url="/tasks", json=task_data_without_completion.model_dump(mode="json")
        )
        assert response.status_code == status.HTTP_201_CREATED

        task_data = TaskReadSchema(**response.json())

        assert task_data.id is not None
        assert task_data.title == task_data_without_completion.title
        assert task_data.description == task_data_without_completion.description
        assert task_data.is_completed is False
        assert task_data.completion == 0

        task_db = await TaskDAO.find_one_or_none(
            TaskModel.id == task_data.id, session=session
        )
        assert task_db is not None
        assert task_db.title == task_data.title
        assert task_db.description == task_data.description
        assert task_db.is_completed is False
        assert task_db.time_to_complete is None
        assert task_db.created_at is not None
        assert task_db.updated_at is not None

        background_task.assert_not_called()

    async def test_create_task_with_completion(
        self,
        session: AsyncSession,
        router_client: httpx.AsyncClient,
        task_data_with_completion: TaskCreateSchema,
        mocker,
    ):
        """Возможно создать задачу c указанием параметра `time_to_complete`."""

        background_task = mocker.patch(
            "src.tasks.service.TaskService._update_task_status_in_background",
            return_value=None,
        )

        response = await router_client.post(
            url="/tasks", json=task_data_with_completion.model_dump(mode="json")
        )
        assert response.status_code == status.HTTP_201_CREATED

        task_data = TaskReadSchema(**response.json())

        assert task_data.id is not None
        assert task_data.title == task_data_with_completion.title
        assert task_data.description == task_data_with_completion.description
        assert task_data.is_completed is False
        assert task_data.completion == 0

        task_db = await TaskDAO.find_one_or_none(
            TaskModel.id == task_data.id, session=session
        )
        assert task_db is not None
        assert task_db.title == task_data.title
        assert task_db.description == task_data.description
        assert task_db.is_completed is False
        assert task_db.time_to_complete == task_data_with_completion.time_to_complete
        assert task_db.created_at is not None
        assert task_db.updated_at is not None

        background_task.assert_called_once_with(
            task_id=task_data.id,
            time_to_complete=task_data_with_completion.time_to_complete,
            session=session,
        )

    # MARK: Put
    async def test_update_task(
        self,
        router_client: httpx.AsyncClient,
        task_db_not_completed: TaskModel,
        task_data_update: TaskUpdateSchema,
    ):
        """Возможно обновить задачу по id."""

        response = await router_client.put(
            url="/tasks",
            params={"task_id": task_db_not_completed.id},
            json=task_data_update.model_dump(mode="json"),
        )
        assert response.status_code == status.HTTP_200_OK

        task_data = TaskReadSchema(**response.json())

        assert task_data.id == task_db_not_completed.id
        assert task_data.title == task_data_update.title
        assert task_data.description == task_data_update.description
        assert task_data.is_completed is True
        assert task_data.completion == 100

    # MARK: Delete
    async def test_delete_task(
        self,
        session: AsyncSession,
        router_client: httpx.AsyncClient,
        task_db_not_completed: TaskModel,
    ):
        """Возможно удалить задачу по id."""

        response = await router_client.delete(
            url="/tasks",
            params={"task_id": task_db_not_completed.id},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        task_db = await TaskDAO.find_one_or_none(
            TaskModel.id == task_db_not_completed.id, session=session
        )
        assert task_db is None
