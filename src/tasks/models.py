import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.api_constants import CURRENT_TIMESTAMP_UTC
from src.database import Base


class TaskModel(Base):
    """Модель задач."""

    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(comment="Заголовок задачи")
    description: Mapped[str | None] = mapped_column(
        nullable=True, comment="Описание задачи"
    )
    is_completed: Mapped[bool] = mapped_column(
        default=False, comment="Статус выполнения задачи"
    )
    to_be_completed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        comment="Дата и время завершения задачи",
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=CURRENT_TIMESTAMP_UTC,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=CURRENT_TIMESTAMP_UTC,
        onupdate=CURRENT_TIMESTAMP_UTC,
    )
