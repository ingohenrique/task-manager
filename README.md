# 📝 Task Manager

Sistema de gerenciamento de tarefas com **FastAPI**, **React**, **PostgreSQL** e **RabbitMQ**.

## 🛠️ Tecnologias

**Backend:**

- FastAPI + Python 3.11
- PostgreSQL + SQLAlchemy
- RabbitMQ + Pika
- pytest + coverage

**Frontend:**

- React 18
- Axios

**Infraestrutura:**

- Docker + Docker Compose
- GitHub Actions CI/CD
- UV (package manager)

## 🚀 Como usar

```bash
git clone <repository-url>
cd task-manager
```

### Desenvolvimento Local

```bash
make setup  # Cria venv + instala dependências
make test   # Executar testes
make lint   # Verificar código
```

**Requirements:** Python 3.11+, UV

### Docker (Produção)

```bash
make up     # Inicia todos os serviços
```

**Requirements:** Docker, Docker Compose

### Comandos disponíveis

```bash
make help   # Ver todos os comandos
```

## 🔗 Endpoints

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api
- **Docs (Swagger):** http://localhost:8000/docs

## ⚙️ Configuração

### CI/CD (GitHub Secrets):

```env
DOCKER_USERNAME=seu_usuario_docker
DOCKER_PASSWORD=sua_senha_docker
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
```

## 📋 API Endpoints

```
GET    /api/tasks/           # Listar tarefas
POST   /api/tasks/           # Criar tarefa
PUT    /api/tasks/{id}       # Atualizar tarefa
DELETE /api/tasks/{id}       # Deletar tarefa
GET    /api/health/          # Health check
```

---
