#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="$ROOT_DIR/.env"
if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1091
  source "$ENV_FILE"
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Erro: comando obrigatorio nao encontrado: python3"
  exit 1
fi

python3 "$SCRIPT_DIR/create_admin_indicacao_test.py"
