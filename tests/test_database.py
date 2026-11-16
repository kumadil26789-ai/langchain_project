import sqlite3
import tempfile
import unittest
from pathlib import Path

from database import MAX_ROWS, execute_read_query, initialize_database


class DatabaseQueryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "company.db"
        initialize_database(self.database_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_select_returns_employee_rows(self) -> None:
        rows = execute_read_query(
            "SELECT name, department FROM employees WHERE department = 'Engineering'",
            self.database_path,
        )
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["name"], "Ava Patel")

    def test_rejects_multiple_statements(self) -> None:
        with self.assertRaises(ValueError):
            execute_read_query(
                "SELECT name FROM employees; DROP TABLE employees",
                self.database_path,
            )

    def test_authorizer_blocks_writes(self) -> None:
        with self.assertRaises(sqlite3.DatabaseError):
            execute_read_query(
                "WITH removed AS (DELETE FROM employees RETURNING id) SELECT * FROM removed",
                self.database_path,
            )
        rows = execute_read_query("SELECT COUNT(*) AS count FROM employees", self.database_path)
        self.assertEqual(rows[0]["count"], 6)

    def test_only_employees_table_can_be_read(self) -> None:
        with self.assertRaises(sqlite3.DatabaseError):
            execute_read_query("SELECT name FROM sqlite_master", self.database_path)

    def test_results_are_capped(self) -> None:
        rows = execute_read_query(
            f"SELECT name FROM employees LIMIT {MAX_ROWS + 10}", self.database_path
        )
        self.assertLessEqual(len(rows), MAX_ROWS)


if __name__ == "__main__":
    unittest.main()
