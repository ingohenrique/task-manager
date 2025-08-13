class TestTaskAPI:
    def test_create_task(self, client, sample_task_data):
        """Test creating a task via API."""
        response = client.post("/api/tasks/", json=sample_task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["titulo"] == sample_task_data["titulo"]
        assert data["descricao"] == sample_task_data["descricao"]
        assert data["status"] == "pendente"
        assert "id" in data
        assert "data_criacao" in data

    def test_create_task_missing_title(self, client):
        """Test creating task without required title."""
        task_data = {"descricao": "Description without title"}

        response = client.post("/api/tasks/", json=task_data)

        assert response.status_code == 422

    def test_create_task_title_too_long(self, client):
        """Test creating task with title too long."""
        task_data = {
            "titulo": "a" * 201,  # Exceeds 200 char limit
            "descricao": "Valid description",
        }

        response = client.post("/api/tasks/", json=task_data)

        assert response.status_code == 422

    def test_get_all_tasks(self, client, sample_task):
        """Test getting all tasks."""
        response = client.get("/api/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        task_ids = [task["id"] for task in data]
        assert sample_task.id in task_ids

    def test_get_tasks_with_pagination(self, client):
        """Test getting tasks with pagination parameters."""
        # Create multiple tasks
        for i in range(5):
            client.post(
                "/api/tasks/",
                json={"titulo": f"Task {i}", "descricao": f"Description {i}"},
            )

        response = client.get("/api/tasks/?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_task_by_id(self, client, sample_task):
        """Test getting a specific task by ID."""
        response = client.get(f"/api/tasks/{sample_task.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_task.id
        assert data["titulo"] == sample_task.titulo
        assert data["descricao"] == sample_task.descricao

    def test_get_task_not_found(self, client):
        """Test getting a task that doesn't exist."""
        response = client.get("/api/tasks/999")

        assert response.status_code == 404
        data = response.json()
        assert (
            "not found" in data["detail"].lower() or "não encontrada" in data["detail"]
        )

    def test_update_task(self, client, sample_task):
        """Test updating a task."""
        update_data = {
            "titulo": "Updated Title",
            "descricao": "Updated description",
            "status": "concluida",
        }

        response = client.put(f"/api/tasks/{sample_task.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["titulo"] == "Updated Title"
        assert data["descricao"] == "Updated description"
        assert data["status"] == "concluida"

    def test_update_task_partial(self, client, sample_task):
        """Test partially updating a task."""
        update_data = {"titulo": "Partially Updated Title"}

        response = client.put(f"/api/tasks/{sample_task.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["titulo"] == "Partially Updated Title"
        assert data["descricao"] == sample_task.descricao

    def test_update_task_not_found(self, client):
        """Test updating a task that doesn't exist."""
        update_data = {"titulo": "New Title"}

        response = client.put("/api/tasks/999", json=update_data)

        assert response.status_code == 404

    def test_update_task_invalid_status(self, client, sample_task):
        """Test updating task with invalid status."""
        update_data = {"status": "invalid_status"}

        response = client.put(f"/api/tasks/{sample_task.id}", json=update_data)

        assert response.status_code == 422

    def test_delete_task(self, client, sample_task):
        """Test deleting a task."""
        response = client.delete(f"/api/tasks/{sample_task.id}")

        assert response.status_code == 204

        get_response = client.get(f"/api/tasks/{sample_task.id}")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client):
        """Test deleting a task that doesn't exist."""
        response = client.delete("/api/tasks/999")

        assert response.status_code == 404


class TestHealthAPI:
    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/api/health/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "task-manager"

    def test_database_health_check(self, client):
        """Test database health check endpoint."""
        response = client.get("/api/health/db")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data


class TestRootAPI:
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
