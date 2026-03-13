#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"
MAIN_FILE="${PROJECT_ROOT}/src/main.py"

echo "==> Project root: ${PROJECT_ROOT}"

if command -v python3.13 >/dev/null 2>&1; then
  PYTHON_BIN="python3.13"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "Error: Python 3 is not installed or not in PATH."
  exit 1
fi

echo "==> Using Python: $(${PYTHON_BIN} --version)"

if [ ! -d "${VENV_DIR}" ]; then
  echo "==> Creating virtual environment in ${VENV_DIR}"
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
else
  echo "==> Virtual environment already exists"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "==> Upgrading pip"
python -m pip install --upgrade pip

if [ -f "${PROJECT_ROOT}/pyproject.toml" ]; then
  echo "==> Installing project dependencies"
  pip install -e "${PROJECT_ROOT}"
else
  echo "Error: pyproject.toml not found in project root."
  exit 1
fi

if [ ! -f "${MAIN_FILE}" ]; then
  echo "Error: ${MAIN_FILE} not found."
  exit 1
fi

echo "==> Starting application"
python "${MAIN_FILE}"