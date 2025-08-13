"""Configuração de fixtures para testes de integração."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from main import app

# Database de teste em memória
TEST_DATABASE_URL = "sqlite:///./test_integration.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override da função get_db para usar banco de teste."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def test_app():
    """Fixture que configura o app para testes de integração."""
    # Criar tabelas
    Base.metadata.create_all(bind=engine)

    # Override da dependência do banco
    app.dependency_overrides[get_db] = override_get_db

    yield app

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app):
    """Cliente de teste HTTP."""
    return TestClient(test_app)


@pytest.fixture
def db_session():
    """Sessão de banco de dados para testes."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def clean_database():
    """Limpa o banco antes de cada teste."""
    # Deleta todos os dados
    connection = engine.connect()
    for table in reversed(Base.metadata.sorted_tables):
        connection.execute(table.delete())
    connection.commit()
    connection.close()
