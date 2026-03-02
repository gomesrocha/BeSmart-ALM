# 🐛 Bug Corrigido - Login Error

## Problema Identificado

O login estava falhando com o erro:
```
TypeError: expected a datetime.date or datetime.datetime instance, got 'str'
invalid input for query argument $1: 'now()'
```

## Causa

O `TimestampMixin` em `services/shared/models/base.py` estava usando:
```python
sa_column_kwargs={"server_default": "now()", "onupdate": "now()"}
```

A string `"now()"` estava sendo passada como valor Python ao invés de uma função SQL.

## Solução Aplicada

Corrigido em `services/shared/models/base.py`:

```python
from sqlalchemy import text

class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("now()")},  # ✅ Usa text()
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("now()"),  # ✅ Usa text()
            "onupdate": datetime.utcnow       # ✅ Usa função Python
        },
    )
```

## Como Aplicar a Correção

### 1. Parar o Backend

```bash
# Encontrar o processo
lsof -i :8086

# Matar o processo
kill -9 <PID>

# Ou usar Ctrl+C no terminal onde está rodando
```

### 2. Reiniciar o Backend

```bash
make dev

# Ou manualmente:
uv run uvicorn services.api_gateway.main:app --reload --port 8086
```

### 3. Testar o Login

1. Abrir http://localhost:3000
2. Fazer login com:
   ```
   Email: admin@test.com
   Senha: admin123456
   ```
3. Deve funcionar agora! ✅

## Verificação

Se o login ainda falhar, pode ser necessário recriar as migrações:

```bash
# Parar backend
kill -9 <PID>

# Resetar banco
docker compose down -v
docker compose up -d
sleep 10

# Recriar migração
rm -rf alembic/versions/*
uv run alembic revision --autogenerate -m "fix timestamp fields"
uv run alembic upgrade head

# Popular dados
make seed

# Reiniciar backend
make dev
```

## Status

✅ **Bug corrigido**
✅ **Código atualizado**
⏳ **Aguardando reinício do backend**

---

**Próximo passo**: Reiniciar o backend e testar o login!
