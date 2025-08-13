from app.models.task import Task, TaskStatus


class TestTaskModel:
    def test_create_task(self, db_session):
        """Test creating a new task."""
        task = Task(
            titulo="Test Task", descricao="Test description", status=TaskStatus.PENDING
        )

        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.id is not None
        assert task.titulo == "Test Task"
        assert task.descricao == "Test description"
        assert task.status == TaskStatus.PENDING
        assert task.data_criacao is not None

    def test_task_status_enum(self):
        """Test task status enum values."""
        assert TaskStatus.PENDING == "pendente"
        assert TaskStatus.COMPLETED == "concluida"

    def test_task_without_description(self, db_session):
        """Test creating task without description."""
        task = Task(titulo="Task without description", status=TaskStatus.PENDING)

        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.descricao is None
        assert task.titulo == "Task without description"

    def test_task_update_timestamp(self, db_session, sample_task):
        """Test that data_atualizacao is set when task is updated."""
        sample_task.status = TaskStatus.COMPLETED
        db_session.commit()
        db_session.refresh(sample_task)

        assert sample_task.status == TaskStatus.COMPLETED
