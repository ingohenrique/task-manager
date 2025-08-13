# Testes de Integração

Este diretório contém os testes de integração do sistema de gerenciamento de tarefas.

## Estrutura

- **`conftest.py`** - Configurações e fixtures para testes de integração
- **`test_api_integration.py`** - Testes de integração da API completa
- **`test_database_integration.py`** - Testes de integração do banco de dados
- **`test_service_integration.py`** - Testes de integração dos serviços

## Tipos de Testes

### 1. Testes de API (`test_api_integration.py`)

Testam o fluxo completo da API REST:

- ✅ Criação de tarefas via HTTP
- ✅ Listagem com dados no banco
- ✅ Busca por ID
- ✅ Atualização completa
- ✅ Remoção via API
- ✅ Tratamento de erros (404, 422)
- ✅ Validação de dados
- ✅ Fluxo de status (pendente → concluída)
- ✅ Health checks

### 2. Testes de Banco de Dados (`test_database_integration.py`)

Testam operações diretas no banco:

- ✅ Persistência completa de tarefas
- ✅ Repositório integrado (CRUD)
- ✅ Múltiplas tarefas simultâneas
- ✅ Comportamento de timestamps
- ✅ Constraints de status
- ✅ Funcionalidades de busca
- ✅ Rollback de transações
- ✅ Atualizações concorrentes

### 3. Testes de Serviços (`test_service_integration.py`)

Testam a integração entre serviços:

- ✅ Criação com notificações RabbitMQ
- ✅ Conclusão com notificação Teams
- ✅ Atualizações sem mudança de status
- ✅ Remoção com eventos
- ✅ Listagem completa
- ✅ Cenários de erro (não encontrado)
- ✅ Fluxo completo (criar → atualizar → completar → deletar)

## Configuração

### Banco de Dados

- Usa SQLite em memória para isolamento
- Cada teste executa em transação isolada
- Limpeza automática entre testes
- Override da dependência `get_db`

### Fixtures Principais

- **`test_app`** - Aplicação FastAPI configurada para testes
- **`client`** - Cliente HTTP para testes de API
- **`db_session`** - Sessão de banco isolada
- **`clean_database`** - Limpeza automática entre testes

## Execução

```bash
# Apenas testes de integração
make test-integration

# Apenas testes unitários
make test-unit

# Todos os testes
make test
```

## Características

### Isolamento

- Cada teste executa em ambiente limpo
- Banco de dados isolado por teste
- Sem interferência entre testes

### Realismo

- Testa fluxo completo da aplicação
- Usa cliente HTTP real
- Banco de dados real (SQLite)
- Testa integrações entre camadas

### Cobertura

- **27 testes** de integração
- **70 testes** total (unit + integration)
- **79% cobertura** de código
- Testa cenários de sucesso e erro

### Performance

- Execução em ~1.8s
- Banco em memória (rápido)
- Paralelização possível com pytest-xdist

## Vantagens dos Testes de Integração

1. **Confiança**: Testam o sistema real funcionando
2. **Detecção de Bugs**: Encontram problemas de integração
3. **Documentação**: Servem como especificação viva
4. **Regressão**: Previnem quebras em mudanças
5. **API Contract**: Validam contratos da API
6. **Fluxos Completos**: Testam user journeys reais
