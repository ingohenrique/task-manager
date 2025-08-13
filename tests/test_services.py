from unittest.mock import Mock, patch

import pytest

from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.rabbitmq_service import RabbitMQService
from app.services.task_service import TaskService
from app.services.teams_service import TeamsService


class TestTaskService:
    def test_create_task(self, db_session):
        """Test creating a task through service."""
        service = TaskService(db_session)
        task_data = TaskCreate(
            titulo="Service Test Task", descricao="Service test description"
        )

        with patch(
            "app.services.task_service.rabbitmq_service.publish_task_event"
        ) as mock_publish:
            task_response = service.create_task(task_data)

            assert task_response.titulo == "Service Test Task"
            assert task_response.descricao == "Service test description"
            assert task_response.status == TaskStatus.PENDING

            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == "task_created"

    def test_get_task(self, db_session, sample_task):
        """Test getting a task through service."""
        service = TaskService(db_session)

        task_response = service.get_task(sample_task.id)

        assert task_response is not None
        assert task_response.id == sample_task.id
        assert task_response.titulo == sample_task.titulo

    def test_get_nonexistent_task(self, db_session):
        """Test getting a task that doesn't exist."""
        service = TaskService(db_session)

        task_response = service.get_task(999)

        assert task_response is None

    def test_get_all_tasks(self, db_session):
        """Test getting all tasks through service."""
        service = TaskService(db_session)

        # Create a task first
        task_data = TaskCreate(titulo="Test Task")
        service.create_task(task_data)

        with patch("app.services.task_service.rabbitmq_service.publish_task_event"):
            tasks = service.get_all_tasks()

            assert len(tasks) >= 1
            assert all(hasattr(task, "id") for task in tasks)

    @pytest.mark.asyncio
    async def test_update_task_status_to_completed(self, db_session, sample_task):
        """Test updating task status to completed sends Teams notification."""
        service = TaskService(db_session)

        update_data = TaskUpdate(status=TaskStatus.COMPLETED)

        with (
            patch(
                "app.services.task_service.teams_service.send_task_completion_notification"
            ) as mock_teams,
            patch(
                "app.services.task_service.rabbitmq_service.publish_task_event"
            ) as mock_publish,
        ):
            updated_task = await service.update_task(sample_task.id, update_data)

            assert updated_task.status == TaskStatus.COMPLETED

            mock_teams.assert_called_once()

            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == "task_updated"

    @pytest.mark.asyncio
    async def test_update_task_other_fields(self, db_session, sample_task):
        """Test updating task fields other than status."""
        service = TaskService(db_session)

        update_data = TaskUpdate(titulo="Updated Title")

        with (
            patch(
                "app.services.task_service.teams_service.send_task_completion_notification"
            ) as mock_teams,
            patch(
                "app.services.task_service.rabbitmq_service.publish_task_event"
            ) as mock_publish,
        ):
            updated_task = await service.update_task(sample_task.id, update_data)

            assert updated_task.titulo == "Updated Title"

            mock_teams.assert_not_called()

            mock_publish.assert_called_once()

    def test_delete_task(self, db_session, sample_task):
        """Test deleting a task through service."""
        service = TaskService(db_session)

        with patch(
            "app.services.task_service.rabbitmq_service.publish_task_event"
        ) as mock_publish:
            success = service.delete_task(sample_task.id)

            assert success is True

            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == "task_deleted"


class TestTeamsService:
    @pytest.mark.asyncio
    async def test_send_task_completion_notification_success(self):
        """Test successful Teams notification."""
        task_data = {
            "id": 1,
            "titulo": "Test Task",
            "descricao": "Test description",
            "data_criacao": "2023-01-01T10:00:00",
            "data_atualizacao": "2023-01-01T11:00:00",
        }

        with (
            patch(
                "app.services.teams_service.settings.teams_webhook_url",
                "http://test-webhook.com",
            ),
            patch("httpx.AsyncClient.post") as mock_post,
        ):
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            await TeamsService.send_task_completion_notification(task_data)

            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert (
                call_args[1]["json"]["sections"][0]["activityTitle"]
                == "✅ Tarefa Concluída"
            )

    @pytest.mark.asyncio
    async def test_send_notification_no_webhook_url(self):
        """Test Teams notification when webhook URL is not configured."""
        task_data = {"id": 1, "titulo": "Test Task"}

        with (
            patch("app.services.teams_service.settings.teams_webhook_url", None),
            patch("httpx.AsyncClient.post") as mock_post,
        ):
            await TeamsService.send_task_completion_notification(task_data)

            mock_post.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_notification_http_error(self):
        """Test Teams notification with HTTP error."""
        task_data = {"id": 1, "titulo": "Test Task"}

        with (
            patch(
                "app.services.teams_service.settings.teams_webhook_url",
                "http://test-webhook.com",
            ),
            patch("httpx.AsyncClient.post") as mock_post,
            patch("app.services.teams_service.logger.error") as mock_log,
        ):
            mock_post.side_effect = Exception("HTTP Error")

            await TeamsService.send_task_completion_notification(task_data)

            mock_log.assert_called_once()


class TestRabbitMQService:
    def test_publish_task_event(self):
        """Test publishing task event."""
        service = RabbitMQService()

        with (
            patch.object(service, "channel") as mock_channel,
            patch.object(service, "connect"),
        ):
            mock_channel.basic_publish = Mock()

            event_type = "task_created"
            task_data = {"id": 1, "titulo": "Test Task"}

            service.publish_task_event(event_type, task_data)

            mock_channel.basic_publish.assert_called_once()

    def test_publish_event_no_connection(self):
        """Test publishing event when not connected."""
        service = RabbitMQService()

        with patch.object(service, "connect") as mock_connect:
            service.channel = None

            service.publish_task_event("test_event", {"test": "data"})

            mock_connect.assert_called_once()

    def test_publish_event_error(self):
        """Test publishing event with error."""
        service = RabbitMQService()

        with (
            patch.object(service, "channel") as mock_channel,
            patch("app.services.rabbitmq_service.logger.error") as mock_log,
        ):
            mock_channel.basic_publish.side_effect = Exception("RabbitMQ Error")

            service.publish_task_event("test_event", {"test": "data"})

            mock_log.assert_called_once()
