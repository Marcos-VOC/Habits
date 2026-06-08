#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
VENV_DIR="$ROOT_DIR/.venv"
PYTHON="${PYTHON:-python3}"
LOCAL_BIN="$HOME/.local/bin"
COMMAND_PATH="$LOCAL_BIN/habits"
DATA_DIR="$HOME/.local/share/habits"
CONFIG_DIR="$HOME/.config/habits"

ensure_venv() {
    if [ ! -x "$VENV_DIR/bin/python" ]; then
        "$PYTHON" -m venv "$VENV_DIR"
    fi
    if ! "$VENV_DIR/bin/python" -m pip --version >/dev/null 2>&1; then
        "$VENV_DIR/bin/python" -m ensurepip --upgrade >/dev/null
    fi
    "$VENV_DIR/bin/python" -m pip install --upgrade pip >/dev/null
}

install_deps() {
    ensure_venv
    "$VENV_DIR/bin/python" -m pip install -e "$ROOT_DIR" >/dev/null
}

install_app() {
    install_deps
    mkdir -p "$LOCAL_BIN"
    cat > "$COMMAND_PATH" <<EOF
#!/usr/bin/env sh
exec "$VENV_DIR/bin/habits" "\$@"
EOF
    chmod +x "$COMMAND_PATH"
    printf 'Habits instalado em %s\n' "$COMMAND_PATH"
    case ":$PATH:" in
        *":$LOCAL_BIN:"*) ;;
        *) printf 'Aviso: %s nao esta no PATH. Reinicie a sessao ou ajuste seu PATH.\n' "$LOCAL_BIN" ;;
    esac
}

uninstall_app() {
    rm -f "$COMMAND_PATH"
    printf 'Comando removido: %s\n' "$COMMAND_PATH"
    printf 'Deseja remover tambem dados e configuracoes? [s/N] '
    read answer
    case "$answer" in
        s|S|sim|SIM|yes|YES)
            rm -rf "$DATA_DIR" "$CONFIG_DIR"
            printf 'Dados removidos.\n'
            ;;
        *)
            printf 'Dados mantidos em:\n- %s\n- %s\n' "$DATA_DIR" "$CONFIG_DIR"
            ;;
    esac
}

run_tests() {
    ensure_venv
    "$VENV_DIR/bin/python" -m pip install -r "$ROOT_DIR/requirements-dev.txt" >/dev/null
    "$VENV_DIR/bin/python" -m pytest "$ROOT_DIR/tests"
}

case "${1:-}" in
    install)
        install_app
        ;;
    uninstall)
        uninstall_app
        ;;
    test)
        run_tests
        ;;
    *)
        install_deps
        "$VENV_DIR/bin/habits" "$@"
        ;;
esac
