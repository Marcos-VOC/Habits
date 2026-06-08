from habits.main import resolve_command


def test_aliases():
    assert resolve_command(["hoje"]) == "today"
    assert resolve_command(["today"]) == "today"
    assert resolve_command(["registrar"]) == "check"
    assert resolve_command(["check"]) == "check"
    assert resolve_command(["sequencia"]) == "streak"
    assert resolve_command(["streak"]) == "streak"
    assert resolve_command(["banco"]) == "db"
    assert resolve_command(["db"]) == "db"
    assert resolve_command(["caminhos"]) == "paths"
    assert resolve_command(["paths"]) == "paths"
