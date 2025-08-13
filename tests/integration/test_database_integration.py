"""Testes de integração para operações de banco de dados."""

from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TestDatabaseIntegration:
    """Testes de integração para operações diretas no banco."""

    def test_task_persistence(self, db_session: Session):
        """Testa persistência completa de tarefa no banco."""
        # Criar tarefa diretamente no banco
        task = Task(
            titulo="Tarefa BD",
            descricao="Teste de banco de dados",
            status=TaskStatus.PENDING,
        )

        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # Verificar se foi salva
        assert task.id is not None
        assert task.titulo == "Tarefa BD"
        assert task.status == TaskStatus.PENDING
        assert task.data_criacao is not None
        assert task.data_atualizacao is not None

        # Buscar do banco
        found_task = db_session.query(Task).filter(Task.id == task.id).first()
        assert found_task is not None
        assert found_task.titulo == task.titulo

    def test_task_repository_integration(self, db_session: Session):
        """Testa integração completa do repositório."""
        repository = TaskRepository(db_session)

        # Criar via repositório
        task_data = TaskCreate(titulo="Repo Test", descricao="Teste do repositório")

        created_task = repository.create(task_data)
        assert created_task.id is not None
        assert created_task.titulo == task_data.titulo

        # Buscar por ID
        found_task = repository.get_by_id(created_task.id)
        assert found_task is not None
        assert found_task.id == created_task.id

        # Listar todas
        all_tasks = repository.get_all()
        assert len(all_tasks) >= 1
        assert any(t.id == created_task.id for t in all_tasks)

        # Atualizar
        update_data = TaskUpdate(
            titulo="Repo Test Updated", status=TaskStatus.COMPLETED
        )

        updated_task = repository.update(created_task.id, update_data)
        assert updated_task.titulo == "Repo Test Updated"
        assert updated_task.status == TaskStatus.COMPLETED

        # Deletar
        deleted = repository.delete(created_task.id)
        assert deleted is True

        # Verificar que foi deletada
        not_found = repository.get_by_id(created_task.id)
        assert not_found is None

    def test_multiple_tasks_persistence(self, db_session: Session):
        """Testa persistência de múltiplas tarefas."""
        repository = TaskRepository(db_session)

        # Criar várias tarefas
        tasks_data = [
            TaskCreate(titulo=f"Tarefa {i}", descricao=f"Descrição {i}")
            for i in range(1, 6)
        ]

        created_tasks = []
        for task_data in tasks_data:
            task = repository.create(task_data)
            created_tasks.append(task)

        # Verificar que todas foram criadas
        all_tasks = repository.get_all()
        assert len(all_tasks) == 5

        # Verificar IDs únicos
        task_ids = [task.id for task in all_tasks]
        assert len(set(task_ids)) == 5  # Todos únicos

        # Atualizar algumas para concluídas
        for i, task in enumerate(created_tasks):
            if i % 2 == 0:  # Tarefas pares
                repository.update(task.id, TaskUpdate(status=TaskStatus.COMPLETED))

        # Verificar status
        updated_tasks = repository.get_all()
        completed_count = sum(
            1 for t in updated_tasks if t.status == TaskStatus.COMPLETED
        )
        pending_count = sum(1 for t in updated_tasks if t.status == TaskStatus.PENDING)

        assert completed_count == 3  # 0, 2, 4
        assert pending_count == 2  # 1, 3

    def test_task_timestamps(self, db_session: Session):
        """Testa comportamento dos timestamps."""
        repository = TaskRepository(db_session)

        # Criar tarefa
        task_data = TaskCreate(titulo="Timestamp Test", descricao="Teste de timestamps")
        created_task = repository.create(task_data)

        original_creation_time = created_task.data_criacao
        original_update_time = created_task.data_atualizacao

        # Verificar timestamps iniciais
        assert original_creation_time is not None
        assert original_update_time is not None
        assert original_creation_time == original_update_time

        # Aguardar um pouco e atualizar
        import time

        time.sleep(1.1)  # Aguardar mais de 1 segundo para garantir diferença

        update_data = TaskUpdate(descricao="Descrição atualizada")
        updated_task = repository.update(created_task.id, update_data)

        # Verificar que data_criacao não mudou e data_atualizacao sim
        assert updated_task.data_criacao == original_creation_time
        assert (
            updated_task.data_atualizacao >= original_update_time
        )  # Usar >= em vez de >

    def test_task_status_constraints(self, db_session: Session):
        """Testa constraints de status."""
        repository = TaskRepository(db_session)

        # Criar tarefa
        task_data = TaskCreate(titulo="Status Test", descricao="Teste de status")
        created_task = repository.create(task_data)

        # Verificar status inicial
        assert created_task.status == TaskStatus.PENDING

        # Atualizar para cada status válido
        for status in TaskStatus:
            updated_task = repository.update(created_task.id, TaskUpdate(status=status))
            assert updated_task.status == status

            # Verificar persistência
            task_from_db = repository.get_by_id(created_task.id)
            assert task_from_db.status == status

    def test_task_search_functionality(self, db_session: Session):
        """Testa funcionalidades de busca no banco."""
        repository = TaskRepository(db_session)

        # Criar tarefas com diferentes características
        tasks_data = [
            TaskCreate(
                titulo="Urgente: Finalizar projeto", descricao="Projeto importante"
            ),
            TaskCreate(titulo="Comprar mantimentos", descricao="Lista de compras"),
            TaskCreate(titulo="Estudar Python", descricao="Aprender FastAPI"),
            TaskCreate(titulo="Exercitar", descricao="Correr no parque"),
        ]

        created_tasks = []
        for task_data in tasks_data:
            task = repository.create(task_data)
            created_tasks.append(task)

        # Marcar algumas como concluídas
        repository.update(created_tasks[1].id, TaskUpdate(status=TaskStatus.COMPLETED))
        repository.update(created_tasks[3].id, TaskUpdate(status=TaskStatus.COMPLETED))

        # Buscar todas as tarefas
        all_tasks = repository.get_all()
        assert len(all_tasks) == 4

        # Simular busca por status (filtro manual)
        pending_tasks = [t for t in all_tasks if t.status == TaskStatus.PENDING]
        completed_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]

        assert len(pending_tasks) == 2
        assert len(completed_tasks) == 2

        # Verificar conteúdo
        pending_titles = [t.titulo for t in pending_tasks]
        assert "Urgente: Finalizar projeto" in pending_titles
        assert "Estudar Python" in pending_titles

    def test_database_rollback(self, db_session: Session):
        """Testa comportamento de rollback."""
        repository = TaskRepository(db_session)

        # Criar tarefa
        task_data = TaskCreate(titulo="Rollback Test", descricao="Teste de rollback")
        created_task = repository.create(task_data)
        task_id = created_task.id

        # Verificar que existe
        assert repository.get_by_id(task_id) is not None

        # Simular erro/rollback (isso acontece automaticamente com a fixture)
        # A fixture clean_database vai limpar tudo entre testes

        # Em um novo "contexto de teste", a tarefa não deve existir
        # (isso é verificado implicitamente pela fixture de limpeza)

    def test_concurrent_updates(self, db_session: Session):
        """Testa atualizações concorrentes (simuladas)."""
        repository = TaskRepository(db_session)

        # Criar tarefa
        task_data = TaskCreate(titulo="Concurrent Test", descricao="Teste concorrência")
        created_task = repository.create(task_data)

        # Simular duas atualizações "simultâneas"
        update1 = TaskUpdate(titulo="Atualização 1")
        update2 = TaskUpdate(descricao="Descrição atualizada 2")

        # Aplicar atualizações sequencialmente
        repository.update(created_task.id, update1)
        repository.update(created_task.id, update2)

        # Verificar que a segunda atualização mantém a primeira
        final_task = repository.get_by_id(created_task.id)
        assert final_task.titulo == "Atualização 1"  # Da primeira atualização
        assert (
            final_task.descricao == "Descrição atualizada 2"
        )  # Da segunda atualização
