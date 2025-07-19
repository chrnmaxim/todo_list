from fastapi import HTTPException, status


class TaskNotFound(HTTPException):
    """Возникает, если задача не найдена."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
        )
