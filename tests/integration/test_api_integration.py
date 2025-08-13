"""Testes de integração para a API completa."""

from fastapi import status

from app.models.task import TaskStatus


class TestTaskAPIIntegration:
    """Testes de integração para API de tarefas."""

    def test_create_task_full_flow(self, client):
        """Testa criação completa de tarefa via API."""
        task_data = {
            "titulo": "Tarefa de Integração",
            "descricao": "Descrição completa da tarefa",
        }

        response = client.post("/api/tasks/", json=task_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["titulo"] == task_data["titulo"]
        assert data["descricao"] == task_data["descricao"]
        assert data["status"] == TaskStatus.PENDING.value
        assert "id" in data
        assert "data_criacao" in data
        assert "data_atualizacao" in data

    def test_get_all_tasks_integration(self, client):
        """Testa listagem de tarefas com dados no banco."""
        # Criar múltiplas tarefas
        tasks_data = [
            {"titulo": "Tarefa 1", "descricao": "Desc 1"},
            {"titulo": "Tarefa 2", "descricao": "Desc 2"},
            {"titulo": "Tarefa 3", "descricao": "Desc 3"},
        ]

        created_tasks = []
        for task_data in tasks_data:
            response = client.post("/api/tasks/", json=task_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_tasks.append(response.json())

        # Buscar todas as tarefas
        response = client.get("/api/tasks/")
        assert response.status_code == status.HTTP_200_OK

        tasks = response.json()
        assert len(tasks) == 3

        # Verificar se todas as tarefas criadas estão na lista
        task_titles = [task["titulo"] for task in tasks]
        for task_data in tasks_data:
            assert task_data["titulo"] in task_titles

    def test_get_task_by_id_integration(self, client):
        """Testa busca de tarefa por ID."""
        # Criar tarefa
        task_data = {"titulo": "Tarefa Específica", "descricao": "Desc específica"}
        create_response = client.post("/api/tasks/", json=task_data)
        created_task = create_response.json()
        task_id = created_task["id"]

        # Buscar tarefa por ID
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == status.HTTP_200_OK

        task = response.json()
        assert task["id"] == task_id
        assert task["titulo"] == task_data["titulo"]
        assert task["descricao"] == task_data["descricao"]

    def test_update_task_integration(self, client):
        """Testa atualização completa de tarefa."""
        # Criar tarefa
        task_data = {"titulo": "Tarefa Original", "descricao": "Desc original"}
        create_response = client.post("/api/tasks/", json=task_data)
        created_task = create_response.json()
        task_id = created_task["id"]

        # Atualizar tarefa
        update_data = {
            "titulo": "Tarefa Atualizada",
            "descricao": "Descrição atualizada",
            "status": TaskStatus.COMPLETED.value,
        }

        update_response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK

        updated_task = update_response.json()
        assert updated_task["id"] == task_id
        assert updated_task["titulo"] == update_data["titulo"]
        assert updated_task["descricao"] == update_data["descricao"]
        assert updated_task["status"] == update_data["status"]

        # Verificar se foi realmente atualizada no banco
        get_response = client.get(f"/api/tasks/{task_id}")
        task_from_db = get_response.json()
        assert task_from_db["titulo"] == update_data["titulo"]
        assert task_from_db["status"] == update_data["status"]

    def test_delete_task_integration(self, client):
        """Testa remoção completa de tarefa."""
        # Criar tarefa
        task_data = {"titulo": "Tarefa Para Deletar", "descricao": "Será removida"}
        create_response = client.post("/api/tasks/", json=task_data)
        created_task = create_response.json()
        task_id = created_task["id"]

        # Verificar que existe
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == status.HTTP_200_OK

        # Deletar tarefa
        delete_response = client.delete(f"/api/tasks/{task_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verificar que foi removida
        get_response_after = client.get(f"/api/tasks/{task_id}")
        assert get_response_after.status_code == status.HTTP_404_NOT_FOUND

    def test_task_not_found_integration(self, client):
        """Testa comportamento com tarefa inexistente."""
        non_existent_id = 99999

        # GET
        response = client.get(f"/api/tasks/{non_existent_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # PUT
        update_data = {"titulo": "Teste"}
        response = client.put(f"/api/tasks/{non_existent_id}", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # DELETE
        response = client.delete(f"/api/tasks/{non_existent_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_task_data_integration(self, client):
        """Testa validação de dados inválidos."""
        # Título vazio
        invalid_data = {"titulo": "", "descricao": "Desc válida"}
        response = client.post("/api/tasks/", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Sem título
        invalid_data = {"descricao": "Só descrição"}
        response = client.post("/api/tasks/", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Status inválido
        task_data = {"titulo": "Tarefa", "descricao": "Desc"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        invalid_update = {"status": "status_inexistente"}
        response = client.put(f"/api/tasks/{task_id}", json=invalid_update)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_task_status_flow_integration(self, client):
        """Testa fluxo completo de status de tarefa."""
        # Criar tarefa (começa como PENDING)
        task_data = {"titulo": "Tarefa Status Flow", "descricao": "Testando fluxo"}
        create_response = client.post("/api/tasks/", json=task_data)
        task = create_response.json()
        task_id = task["id"]

        assert task["status"] == TaskStatus.PENDING.value

        # Marcar como concluída
        update_data = {"status": TaskStatus.COMPLETED.value}
        update_response = client.put(f"/api/tasks/{task_id}", json=update_data)
        updated_task = update_response.json()

        assert updated_task["status"] == TaskStatus.COMPLETED.value
        # Como pode acontecer no mesmo segundo, verificamos que o timestamp existe
        assert updated_task["data_atualizacao"] is not None

        # Verificar persistência
        get_response = client.get(f"/api/tasks/{task_id}")
        task_from_db = get_response.json()
        assert task_from_db["status"] == TaskStatus.COMPLETED.value


class TestHealthCheckIntegration:
    """Testes de integração para health checks."""

    def test_health_check_api(self, client):
        """Testa health check geral da API."""
        response = client.get("/api/health/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "task-manager"

    def test_database_health_check(self, client):
        """Testa health check do banco de dados."""
        response = client.get("/api/health/db")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"


class TestTaskSearchAndFilter:
    """Testes de integração para busca e filtros."""

    def test_search_tasks_by_status(self, client):
        """Testa busca por status (simulação)."""
        # Criar tarefas com diferentes status
        pending_task = {"titulo": "Pendente", "descricao": "Desc"}
        client.post("/api/tasks/", json=pending_task)

        completed_task_data = {"titulo": "Completa", "descricao": "Desc"}
        create_response = client.post("/api/tasks/", json=completed_task_data)
        completed_task_id = create_response.json()["id"]

        # Marcar como concluída
        client.put(
            f"/api/tasks/{completed_task_id}",
            json={"status": TaskStatus.COMPLETED.value},
        )

        # Buscar todas as tarefas e verificar status
        response = client.get("/api/tasks/")
        tasks = response.json()

        pending_tasks = [t for t in tasks if t["status"] == TaskStatus.PENDING.value]
        completed_tasks = [
            t for t in tasks if t["status"] == TaskStatus.COMPLETED.value
        ]

        assert len(pending_tasks) == 1
        assert len(completed_tasks) == 1
        assert pending_tasks[0]["titulo"] == "Pendente"
        assert completed_tasks[0]["titulo"] == "Completa"
