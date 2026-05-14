#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
PROJECT_DIR="$(cd "$ROOT_DIR/.." && pwd)"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env
fi

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Erro: comando obrigatorio nao encontrado: $1"
    exit 1
  fi
}

require_env() {
  local var_name="$1"
  if [[ -z "${!var_name:-}" ]]; then
    echo "Erro: variavel obrigatoria nao definida: $var_name"
    exit 1
  fi
}

mysql_exec() {
  local sql_file="$1"

  local mysql_args=(
    -h "${MYSQL_HOST}"
    -P "${MYSQL_PORT}"
    -u "${MYSQL_USER}"
  )

  if [[ -n "${MYSQL_PASSWORD}" ]]; then
    mysql_args+=("-p${MYSQL_PASSWORD}")
  fi

  mysql "${mysql_args[@]}" < "$sql_file"
}

echo "[1/6] Validando dependencias de sistema..."
require_cmd python3
require_cmd mysql
require_cmd curl

if command -v docker >/dev/null 2>&1 && command -v docker compose >/dev/null 2>&1; then
  echo "MySQL via Docker disponivel."
else
  echo "Aviso: docker compose nao encontrado. Vou usar MySQL ja disponivel localmente."
fi

echo "[2/6] Validando variaveis de ambiente do MySQL..."
require_env MYSQL_HOST
require_env MYSQL_PORT
require_env MYSQL_USER
require_env MYSQL_DATABASE
: "${MYSQL_PASSWORD:=}"

echo "[3/6] Criando venv e instalando dependencias Python..."
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

echo "[4/6] Garantindo banco MySQL disponivel..."
if command -v docker >/dev/null 2>&1 && command -v docker compose >/dev/null 2>&1 && [[ -f "$PROJECT_DIR/docker-sql.yaml" ]]; then
  (cd "$PROJECT_DIR" && docker compose -f docker-sql.yaml up -d)
  echo "Container MySQL iniciado pelo docker-sql.yaml"
else
  mysql_exec "db/schema.sql"
  echo "Schema aplicado em MySQL local"
fi

echo "[5/6] Criando admin..."
if [[ -n "${ADMIN_NAME:-}" && -n "${ADMIN_EMAIL:-}" && -n "${ADMIN_PASSWORD:-}" ]]; then
  ADMIN_HASH="$(python3 -c 'from werkzeug.security import generate_password_hash; import os; print(generate_password_hash(os.environ["ADMIN_PASSWORD"]))')"

  SQL=$(cat <<EOF
INSERT INTO usuarios (nome, email, senha_hash, papel, status, senha_temporaria)
VALUES ('${ADMIN_NAME}', '${ADMIN_EMAIL}', '${ADMIN_HASH}', 'ADMIN', 'ATIVO', FALSE)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome),
  senha_hash = VALUES(senha_hash),
  papel = 'ADMIN',
  status = 'ATIVO',
  senha_temporaria = FALSE;
EOF
)

  mysql_args=(
    -h "${MYSQL_HOST}"
    -P "${MYSQL_PORT}"
    -u "${MYSQL_USER}"
    "${MYSQL_DATABASE}"
    -e "$SQL"
  )

  if [[ -n "${MYSQL_PASSWORD}" ]]; then
    mysql_args=(
      -h "${MYSQL_HOST}"
      -P "${MYSQL_PORT}"
      -u "${MYSQL_USER}"
      "-p${MYSQL_PASSWORD}"
      "${MYSQL_DATABASE}"
      -e "$SQL"
    )
  fi

  mysql "${mysql_args[@]}"
  echo "Admin criado/atualizado via variaveis ADMIN_*"
else
  echo "ADMIN_* nao definido. Executando criacao interativa de admin..."
  python3 scripts/create_admin.py
fi

echo "[6/6] Subindo app e executando smoke test..."
python3 app.py >/tmp/monitoria-app.log 2>&1 &
APP_PID=$!

cleanup() {
  if ps -p "$APP_PID" >/dev/null 2>&1; then
    kill "$APP_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

curl -fsS --retry 20 --retry-connrefused --retry-delay 1 http://127.0.0.1:5000/health >/tmp/monitoria-health.json
HEALTH_CODE="$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/health)"
LOGIN_CODE="$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/auth/login)"
USERS_CODE="$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/usuarios/)"

if [[ "$HEALTH_CODE" != "200" ]]; then
  echo "Falha: /health retornou $HEALTH_CODE"
  exit 1
fi

if [[ "$LOGIN_CODE" != "200" ]]; then
  echo "Falha: /auth/login retornou $LOGIN_CODE"
  exit 1
fi

if [[ "$USERS_CODE" != "302" ]]; then
  echo "Falha: /usuarios/ deveria redirecionar para login (302), retornou $USERS_CODE"
  exit 1
fi

echo "Smoke test OK"
echo "- GET /health: 200"
echo "- GET /auth/login: 200"
echo "- GET /usuarios/: 302 (protegido por login)"
echo ""
echo "Agora, para rodar manualmente o sistema:"
echo "source .venv/bin/activate && python3 app.py"
echo "Acesse: http://127.0.0.1:5000"
