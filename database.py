import sqlite3
from pathlib import Path
from typing import Any


DATABASE_PATH = Path(__file__).parent / "data" / "company.db"
MAX_ROWS = 100
TABLE_NAME = "employees"

_ALLOWED_ACTIONS = {
    sqlite3.SQLITE_SELECT,
    sqlite3.SQLITE_READ,
    sqlite3.SQLITE_FUNCTION,
    sqlite3.SQLITE_RECURSIVE,
}


def initialize_database(path: Path = DATABASE_PATH) -> None:
    """Create the example employees table and seed it when the database is new."""
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                title TEXT NOT NULL,
                salary INTEGER NOT NULL,
                location TEXT NOT NULL
            )
            """
        )
        count = connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        if count == 0:
            connection.executemany(
                """
                INSERT INTO employees (name, department, title, salary, location)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    ("Ava Patel", "Engineering", "Software Engineer", 115000, "New York"),
                    ("Liam Chen", "Engineering", "Engineering Manager", 148000, "Seattle"),
                    ("Mia Garcia", "Marketing", "Marketing Specialist", 82000, "Austin"),
                    ("Noah Kim", "Sales", "Account Executive", 93000, "Chicago"),
                    ("Sofia Brown", "Human Resources", "HR Generalist", 78000, "New York"),
                    ("Ethan Wilson", "Engineering", "Data Engineer", 121000, "Austin"),
                ],
            )
        connection.commit()
    finally:
        connection.close()


def execute_read_query(
    query: str, path: Path = DATABASE_PATH
) -> list[dict[str, Any]]:
    """Execute a single read-only SELECT against the employees table."""
    statement = query.strip().rstrip(";").strip()
    if not statement or ";" in statement:
        raise ValueError("Only one read-only SELECT statement is allowed.")
    if not statement.lower().startswith(("select ", "with ")):
        raise ValueError("Only read-only SELECT queries are allowed.")

    connection = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row

    def authorize(action: int, first: str | None, second: str | None, *_: Any) -> int:
        if action not in _ALLOWED_ACTIONS:
            return sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_READ and first != TABLE_NAME:
            return sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_FUNCTION and second == "load_extension":
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    try:
        connection.set_authorizer(authorize)
        cursor = connection.execute(statement)
        return [dict(row) for row in cursor.fetchmany(MAX_ROWS)]
    finally:
        connection.close()
