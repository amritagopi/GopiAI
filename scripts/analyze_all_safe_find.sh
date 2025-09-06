#!/usr/bin/env bash
set -euo pipefail

# --- Настройки (при необходимости измени) ---
PROJECT_ROOT="/home/amritagopi/GopiAI"
DEV_VENV="$HOME/venvs/dev-tools"
VENV1="/home/amritagopi/GopiAI/.venv"
VENV2="/home/amritagopi/GopiAI/GopiAI-CrewAI/venv"
REPORTS_DIR="$PROJECT_ROOT/reports"

# относительные пути для исключения (используются в find -not -path)
EXCLUDE_1=".venv"
EXCLUDE_2="GopiAI-CrewAI/venv"

mkdir -p "$REPORTS_DIR"
echo "Reports -> $REPORTS_DIR"

# --- Dev venv: создаём/активируем и ставим инструменты ---
if [ ! -d "$DEV_VENV" ]; then
  echo "Creating dev venv at $DEV_VENV"
  python3 -m venv "$DEV_VENV"
fi

# shellcheck source=/dev/null
source "$DEV_VENV/bin/activate"

python -m pip install --upgrade pip setuptools wheel >/dev/null
python -m pip install --upgrade ruff vulture unimport >/dev/null

echo "Dev tools installed: ruff, vulture, unimport"

# --- 1) Ruff ---
echo "=== Ruff ==="
{
  echo "Ruff report for project: $PROJECT_ROOT"
  echo "Excluded: $EXCLUDE_1, $EXCLUDE_2"
  echo "Run at: $(date --iso-8601=seconds)"
  echo
  # ruff поддерживает --exclude, но всё же указываем названия директорий:
  ruff check "$PROJECT_ROOT" --exclude "$EXCLUDE_1" --exclude "$EXCLUDE_2" || true
} > "$REPORTS_DIR/ruff.txt" 2>&1
echo "Saved -> $REPORTS_DIR/ruff.txt"

# --- 2) Vulture ---
echo "=== Vulture ==="
{
  echo "Vulture report for project: $PROJECT_ROOT"
  echo "Excluded: $EXCLUDE_1, $EXCLUDE_2"
  echo "Run at: $(date --iso-8601=seconds)"
  echo
  vulture "$PROJECT_ROOT" --min-confidence 80 --exclude "$EXCLUDE_1" --exclude "$EXCLUDE_2" || true
} > "$REPORTS_DIR/vulture.txt" 2>&1
echo "Saved -> $REPORTS_DIR/vulture.txt"

# --- 3) Unimport (safe find -> xargs) ---
echo "=== Unimport (safe find -> xargs) ==="
UNIMPORT_OUT="$REPORTS_DIR/unimport.txt"
{
  echo "Unimport report (safe find) for project: $PROJECT_ROOT"
  echo "Excluded patterns: $EXCLUDE_1, $EXCLUDE_2, .git, __pycache__"
  echo "Run at: $(date --iso-8601=seconds)"
  echo

  # Находим все .py файлы, исключая вендоры/кеши/.git, и передаём пакетами по 50 штук в unimport.
  # -print0 + xargs -0 защищает от пробелов в именах.
  find "$PROJECT_ROOT" \
    -type f -name '*.py' \
    -not -path "$PROJECT_ROOT/$EXCLUDE_1/*" \
    -not -path "$PROJECT_ROOT/$EXCLUDE_2/*" \
    -not -path "*/.git/*" \
    -not -path "*/__pycache__/*" \
    -print0 \
  | xargs -0 -n 50 unimport || true

} > "$UNIMPORT_OUT" 2>&1
echo "Saved -> $UNIMPORT_OUT"

# Деактивируем dev venv
deactivate || true

# --- 4) Pylint в target venvs ---
run_pylint_in_venv() {
  VENV_PATH="$1"
  LABEL="$2"
  OUTFILE="$REPORTS_DIR/pylint_${LABEL}.txt"

  if [ ! -d "$VENV_PATH" ] || [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "Skipping pylint for $LABEL — venv not found at $VENV_PATH" | tee "$OUTFILE"
    return
  fi

  echo "=== Pylint in $LABEL ($VENV_PATH) ==="
  # shellcheck source=/dev/null
  source "$VENV_PATH/bin/activate"

  python -m pip install --upgrade pip setuptools >/dev/null
  python -m pip install --upgrade pylint >/dev/null

  {
    echo "Pylint report for project: $PROJECT_ROOT"
    echo "Running in venv: $VENV_PATH"
    echo "Run at: $(date --iso-8601=seconds)"
    echo
    pylint "$PROJECT_ROOT" --exit-zero || true
  } > "$OUTFILE" 2>&1

  echo "Saved -> $OUTFILE"
  deactivate || true
}

run_pylint_in_venv "$VENV1" "dot_venv"
run_pylint_in_venv "$VENV2" "crewai_venv"

echo
echo "Done — reports:"
ls -lh "$REPORTS_DIR" || true
echo
echo "View with:"
echo "  less $REPORTS_DIR/ruff.txt"
echo "  less $REPORTS_DIR/vulture.txt"
echo "  less $REPORTS_DIR/unimport.txt"
echo "  less $REPORTS_DIR/pylint_dot_venv.txt"
echo "  less $REPORTS_DIR/pylint_crewai_venv.txt"

