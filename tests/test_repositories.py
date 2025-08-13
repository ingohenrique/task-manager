from app.models.task import TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TestTaskRepository:
    def test_create_task(self, db_session):
        """Test creating a task through repository."""
        repo = TaskRepository(db_session)
        task_data = TaskCreate(
            titulo="Repository Test Task", descricao="Test description"
        )

        task = repo.create(task_data)

        assert task.id is not None
        assert task.titulo == "Repository Test Task"
        assert task.descricao == "Test description"
        assert task.status == TaskStatus.PENDING

    def test_get_task_by_id(self, db_session, sample_task):
        """Test getting task by ID."""
        repo = TaskRepository(db_session)

        found_task = repo.get_by_id(sample_task.id)

        assert found_task is not None
        assert found_task.id == sample_task.id
        assert found_task.titulo == sample_task.titulo

    def test_get_task_by_invalid_id(self, db_session):
        """Test getting task with invalid ID."""
        repo = TaskRepository(db_session)

        found_task = repo.get_by_id(999)

        assert found_task is None

    def test_get_all_tasks(self, db_session):
        """Test getting all tasks."""
        repo = TaskRepository(db_session)

        # Create multiple tasks
        for i in range(3):
            task_data = TaskCreate(titulo=f"Task {i}", descricao=f"Description {i}")
            repo.create(task_data)

        tasks = repo.get_all()

        assert len(tasks) == 3

    def test_get_all_tasks_with_pagination(self, db_session):
        """Test getting tasks with pagination."""
        repo = TaskRepository(db_session)

        # Create multiple tasks
        for i in range(5):
            task_data = TaskCreate(titulo=f"Task {i}", descricao=f"Description {i}")
            repo.create(task_data)

        tasks = repo.get_all(skip=0, limit=2)
        assert len(tasks) == 2

        tasks = repo.get_all(skip=2, limit=2)
        assert len(tasks) == 2

    def test_update_task(self, db_session, sample_task):
        """Test updating a task."""
        repo = TaskRepository(db_session)

        update_data = TaskUpdate(titulo="Updated Title", status=TaskStatus.COMPLETED)

        updated_task = repo.update(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.titulo == "Updated Title"
        assert updated_task.status == TaskStatus.COMPLETED
        assert updated_task.descricao == sample_task.descricao

    def test_update_nonexistent_task(self, db_session):
        """Test updating a task that doesn't exist."""
        repo = TaskRepository(db_session)

        update_data = TaskUpdate(titulo="New Title")
        updated_task = repo.update(999, update_data)

        assert updated_task is None

    def test_delete_task(self, db_session, sample_task):
        """Test deleting a task."""
        repo = TaskRepository(db_session)

        success = repo.delete(sample_task.id)

        assert success is True

        found_task = repo.get_by_id(sample_task.id)
        assert found_task is None

    def test_delete_nonexistent_task(self, db_session):
        """Test deleting a task that doesn't exist."""
        repo = TaskRepository(db_session)

        success = repo.delete(999)

        assert success is False

    def test_get_by_status(self, db_session):
        """Test getting tasks by status."""
        repo = TaskRepository(db_session)

        # Create tasks with different statuses
        pending_task = TaskCreate(titulo="Pending Task")
        completed_task_data = TaskCreate(titulo="Completed Task")

        repo.create(pending_task)
        completed_task = repo.create(completed_task_data)

        repo.update(completed_task.id, TaskUpdate(status=TaskStatus.COMPLETED))

        pending_tasks = repo.get_by_status(TaskStatus.PENDING)
        assert len(pending_tasks) == 1
        assert pending_tasks[0].titulo == "Pending Task"

        completed_tasks = repo.get_by_status(TaskStatus.COMPLETED)
        assert len(completed_tasks) == 1
        assert completed_tasks[0].titulo == "Completed Task"
