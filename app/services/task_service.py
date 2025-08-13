from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.task import TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.rabbitmq_service import rabbitmq_service
from app.services.teams_service import teams_service


class TaskService:
    def __init__(self, db: Session):
        self.repository = TaskRepository(db)

    def create_task(self, task_data: TaskCreate) -> TaskResponse:
        task = self.repository.create(task_data)

        # Publish event
        rabbitmq_service.publish_task_event(
            "task_created",
            {
                "id": task.id,
                "titulo": task.titulo,
                "status": task.status.value,
                "data_criacao": str(task.data_criacao),
            },
        )

        return TaskResponse.model_validate(task)

    def get_task(self, task_id: int) -> Optional[TaskResponse]:
        task = self.repository.get_by_id(task_id)
        if task:
            return TaskResponse.model_validate(task)
        return None

    def get_all_tasks(self, skip: int = 0, limit: int = 100) -> List[TaskResponse]:
        tasks = self.repository.get_all(skip, limit)
        return [TaskResponse.model_validate(task) for task in tasks]

    async def update_task(
        self, task_id: int, task_data: TaskUpdate
    ) -> Optional[TaskResponse]:
        # Get current task to check status change
        current_task = self.repository.get_by_id(task_id)
        if not current_task:
            return None

        old_status = current_task.status
        task = self.repository.update(task_id, task_data)

        if task:
            # Check if status changed to completed
            if (
                old_status != TaskStatus.COMPLETED
                and task.status == TaskStatus.COMPLETED
            ):
                # Send Teams notification
                await teams_service.send_task_completion_notification(
                    {
                        "id": task.id,
                        "titulo": task.titulo,
                        "descricao": task.descricao,
                        "data_criacao": str(task.data_criacao),
                        "data_atualizacao": str(task.data_atualizacao),
                    }
                )

            # Publish status change event
            rabbitmq_service.publish_task_event(
                "task_updated",
                {
                    "id": task.id,
                    "titulo": task.titulo,
                    "status": task.status.value,
                    "old_status": old_status.value,
                    "data_atualizacao": str(task.data_atualizacao),
                },
            )

            return TaskResponse.model_validate(task)

        return None

    def delete_task(self, task_id: int) -> bool:
        task = self.repository.get_by_id(task_id)
        if task:
            success = self.repository.delete(task_id)
            if success:
                rabbitmq_service.publish_task_event(
                    "task_deleted", {"id": task.id, "titulo": task.titulo}
                )
            return success
        return False
