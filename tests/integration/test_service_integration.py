"""Testes de integração para serviços completos."""

from unittest.mock import AsyncMock, patch

import pytest

from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService


class TestTaskServiceIntegration:
    """Testes de integração para TaskService completo."""

    @pytest.mark.asyncio
    async def test_create_task_with_notifications(self, db_session):
        """Testa criação de tarefa com notificações integradas."""
        service = TaskService(db_session)

        task_data = TaskCreate(
            titulo="Tarefa com Notificação", descricao="Testa integração completa"
        )

        with patch(
            "app.services.task_service.rabbitmq_service.publish_task_event"
        ) as mock_publish:
            created_task = service.create_task(task_data)

            # Verificar tarefa criada
            assert created_task.id is not None
            assert created_task.titulo == task_data.titulo
            assert created_task.status == TaskStatus.PENDING

            # Verificar que evento foi publicado
            mock_publish.assert_called_once_with(
                "task_created",
                {
                    "id": created_task.id,
                    "titulo": created_task.titulo,
                    "status": created_task.status.value,
                    "data_criacao": str(created_task.data_criacao),
                },
            )

    @pytest.mark.asyncio
    async def test_complete_task_with_teams_notification(self, db_session):
        """Testa conclusão com notificação do Teams."""
        service = TaskService(db_session)

        # Criar tarefa
        task_data = TaskCreate(titulo="Tarefa Teams", descricao="Para testar Teams")
        created_task = service.create_task(task_data)

        # Completar tarefa
        update_data = TaskUpdate(status=TaskStatus.COMPLETED)

        with (
            patch(
                "app.services.task_service.teams_service.send_task_completion_notification"
            ) as mock_teams,
            patch(
                "app.services.task_service.rabbitmq_service.publish_task_event"
            ) as mock_publish,
        ):
            mock_teams.return_value = AsyncMock()

            updated_task = await service.update_task(created_task.id, update_data)

            # Verificar atualização
            assert updated_task.status == TaskStatus.COMPLETED

            # Verificar notificação Teams
            mock_teams.assert_called_once()
            teams_call_args = mock_teams.call_args[0][0]
            assert teams_call_args["id"] == created_task.id
            assert teams_call_args["titulo"] == created_task.titulo

            # Verificar evento RabbitMQ
            mock_publish.assert_called_with(
                "task_updated",
                {
                    "id": updated_task.id,
                    "titulo": updated_task.titulo,
                    "status": updated_task.status.value,
                    "old_status": TaskStatus.PENDING.value,
                    "data_atualizacao": str(updated_task.data_atualizacao),
                },
            )

    @pytest.mark.asyncio
    async def test_update_task_without_status_change(self, db_session):
        """Testa atualização sem mudança de status."""
        service = TaskService(db_session)

        # Criar tarefa
        task_data = TaskCreate(titulo="Original", descricao="Desc original")
        created_task = service.create_task(task_data)

        # Atualizar apenas título e descrição
        update_data = TaskUpdate(
            titulo="Título Atualizado", descricao="Descrição atualizada"
        )

        with (
            patch(
                "app.services.task_service.teams_service.send_task_completion_notification"
            ) as mock_teams,
            patch(
                "app.services.task_service.rabbitmq_service.publish_task_event"
            ) as mock_publish,
        ):
            updated_task = await service.update_task(created_task.id, update_data)

            # Verificar atualização
            assert updated_task.titulo == "Título Atualizado"
            assert updated_task.descricao == "Descrição atualizada"
            assert updated_task.status == TaskStatus.PENDING  # Não mudou

            # Teams não deve ser chamado (status não mudou para COMPLETED)
            mock_teams.assert_not_called()

            # RabbitMQ deve ser chamado
            mock_publish.assert_called_once_with(
                "task_updated",
                {
                    "id": updated_task.id,
                    "titulo": updated_task.titulo,
                    "status": updated_task.status.value,
                    "old_status": TaskStatus.PENDING.value,
                    "data_atualizacao": str(updated_task.data_atualizacao),
                },
            )

    def test_delete_task_with_notifications(self, db_session):
        """Testa remoção com notificações."""
        service = TaskService(db_session)

        # Criar tarefa
        task_data = TaskCreate(titulo="Para Deletar", descricao="Será removida")
        created_task = service.create_task(task_data)
        task_id = created_task.id

        # Deletar tarefa
        with patch(
            "app.services.task_service.rabbitmq_service.publish_task_event"
        ) as mock_publish:
            result = service.delete_task(task_id)

            # Verificar remoção
            assert result is True

            # Verificar que não existe mais
            assert service.get_task(task_id) is None

            # Verificar evento
            mock_publish.assert_called_once_with(
                "task_deleted", {"id": task_id, "titulo": "Para Deletar"}
            )

    def test_get_all_tasks_integration(self, db_session):
        """Testa listagem completa de tarefas."""
        service = TaskService(db_session)

        # Criar múltiplas tarefas
        tasks_data = [
            TaskCreate(titulo=f"Tarefa {i}", descricao=f"Descrição {i}")
            for i in range(1, 4)
        ]

        created_tasks = []
        for task_data in tasks_data:
            with patch("app.services.task_service.rabbitmq_service.publish_task_event"):
                task = service.create_task(task_data)
                created_tasks.append(task)

        # Buscar todas
        all_tasks = service.get_all_tasks()

        assert len(all_tasks) == 3

        # Verificar que todas estão na lista
        task_ids = [task.id for task in all_tasks]
        for created_task in created_tasks:
            assert created_task.id in task_ids

    def test_task_not_found_scenarios(self, db_session):
        """Testa cenários de tarefa não encontrada."""
        service = TaskService(db_session)

        non_existent_id = 99999

        # GET
        assert service.get_task(non_existent_id) is None

        # DELETE
        assert service.delete_task(non_existent_id) is False

    @pytest.mark.asyncio
    async def test_update_nonexistent_task(self, db_session):
        """Testa atualização de tarefa inexistente."""
        service = TaskService(db_session)

        update_data = TaskUpdate(titulo="Não existe")

        result = await service.update_task(99999, update_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_complete_workflow_integration(self, db_session):
        """Testa fluxo completo: criar -> atualizar -> completar -> deletar."""
        service = TaskService(db_session)

        # 1. Criar
        task_data = TaskCreate(
            titulo="Fluxo Completo", descricao="Teste de workflow completo"
        )

        with patch("app.services.task_service.rabbitmq_service.publish_task_event"):
            created_task = service.create_task(task_data)
            task_id = created_task.id

        assert created_task.status == TaskStatus.PENDING

        # 2. Atualizar detalhes
        update_data = TaskUpdate(
            titulo="Fluxo Completo - Atualizado", descricao="Descrição atualizada"
        )

        with (
            patch("app.services.task_service.rabbitmq_service.publish_task_event"),
            patch(
                "app.services.task_service.teams_service.send_task_completion_notification"
            ),
        ):
            updated_task = await service.update_task(task_id, update_data)

        assert updated_task.titulo == "Fluxo Completo - Atualizado"
        assert updated_task.status == TaskStatus.PENDING

        # 3. Completar
        complete_data = TaskUpdate(status=TaskStatus.COMPLETED)

        with (
            patch("app.services.task_service.rabbitmq_service.publish_task_event"),
            patch(
                "app.services.task_service.teams_service.send_task_completion_notification"
            ) as mock_teams,
        ):
            mock_teams.return_value = AsyncMock()
            completed_task = await service.update_task(task_id, complete_data)

        assert completed_task.status == TaskStatus.COMPLETED
        mock_teams.assert_called_once()

        # 4. Verificar estado final
        final_task = service.get_task(task_id)
        assert final_task.status == TaskStatus.COMPLETED
        assert final_task.titulo == "Fluxo Completo - Atualizado"

        # 5. Deletar
        with patch("app.services.task_service.rabbitmq_service.publish_task_event"):
            deleted = service.delete_task(task_id)

        assert deleted is True
        assert service.get_task(task_id) is None
