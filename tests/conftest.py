from __future__ import annotations

import sqlite3

import pytest

from habits.db import connect, init_db


@pytest.fixture()
def conn(tmp_path) -> sqlite3.Connection:
    connection = connect(tmp_path / "habits.db")
    init_db(connection)
    try:
        yield connection
    finally:
        connection.close()
