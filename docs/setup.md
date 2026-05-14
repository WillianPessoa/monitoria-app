# Setup de Desenvolvimento Local

Guia para subir o backend localmente.

## 1) Pre-requisitos

- Python 3.12
- Docker + Docker Compose
- pip atualizado

## 2) Criar e ativar ambiente virtual

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

## 3) Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4) Subir banco MySQL em container

```bash
cd ..
docker compose -f docker-sql.yaml up -d
docker compose -f docker-sql.yaml ps
cd backend
```

O schema em `backend/db/schema.sql` e aplicado automaticamente no primeiro start do container.

## 5) Configurar variaveis de ambiente

Exemplo minimo:

```bash
export SECRET_KEY="troque-esta-chave"
export MYSQL_HOST="127.0.0.1"
export MYSQL_PORT="3306"
export MYSQL_USER="root"
export MYSQL_PASSWORD="monitoria_root"
export MYSQL_DATABASE="monitoria_app"

```

## 6) Criar primeiro admin

Use o script auxiliar:

```bash
python scripts/create_admin.py
```

## 7) Rodar aplicacao

```bash
python app.py
```

A aplicacao ficara em http://localhost:5000.

## 7.1) Parar banco em container

```bash
cd ..
docker compose -f docker-sql.yaml down
```

## 8) Smoke test automatico (Sprint 1)

Para validar setup + banco + healthcheck com um comando:

```bash
bash scripts/smoke_test_sprint1.sh
```

Se quiser criar/atualizar admin sem prompt interativo, defina `ADMIN_NAME`, `ADMIN_EMAIL` e `ADMIN_PASSWORD` antes de executar o script.

## Validacao minima entre ambientes

- Linux: setup realizado no dev container do projeto.
- Windows/macOS: seguir o mesmo passo a passo, ajustando ativacao da virtualenv conforme shell local.
