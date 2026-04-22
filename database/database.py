import logging
import sqlite3
import numpy as np
from pathlib import Path
from typing import Optional

from models import Employee

logger = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 1

_MIGRATIONS = {
    1: """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY
        );
        INSERT OR IGNORE INTO schema_version (version) VALUES (1);
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            position TEXT NOT NULL,
            face_encoding BLOB,
            photo_path TEXT
        );
        CREATE TABLE IF NOT EXISTS keys (
            cabinet TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'AVAILABLE',
            holder_id INTEGER,
            holder_name TEXT,
            FOREIGN KEY (holder_id) REFERENCES employees(id)
        );
    """,
}


class Database:
    def __init__(self, db_path: str = "data.db"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._run_migrations()

    def _run_migrations(self):
        current_version = self._get_schema_version()
        
        for version in range(current_version + 1, CURRENT_SCHEMA_VERSION + 1):
            if version in _MIGRATIONS:
                try:
                    self._conn.executescript(_MIGRATIONS[version])
                    logger.info(f"Migration to version {version} completed")
                except Exception as e:
                    logger.error(f"Migration {version} failed: {e}")
                    raise

    def _get_schema_version(self) -> int:
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
            row = cursor.fetchone()
            return row["version"] if row else 0
        except sqlite3.OperationalError:
            return 0

    def add_employee(self, full_name: str, position: str, face_encoding: Optional[bytes] = None, photo_path: Optional[str] = None) -> int:
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO employees (full_name, position, face_encoding, photo_path) VALUES (?, ?, ?, ?)",
            (full_name, position, face_encoding, photo_path)
        )
        self._conn.commit()
        return cursor.lastrowid

    def get_employee(self, emp_id: int) -> Optional[Employee]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
        row = cursor.fetchone()
        if row:
            return self._row_to_employee(row)
        return None

    def get_employee_by_face(self, face_encoding: bytes, threshold: float = 0.6) -> Optional[Employee]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE face_encoding IS NOT NULL")
        rows = cursor.fetchall()
        
        input_encoding = np.frombuffer(face_encoding, dtype=np.float64)
        
        for row in rows:
            stored_encoding = np.frombuffer(row["face_encoding"], dtype=np.float64)
            
            if input_encoding.shape != stored_encoding.shape:
                continue
                
            cosine_sim = np.dot(input_encoding, stored_encoding) / (
                np.linalg.norm(input_encoding) * np.linalg.norm(stored_encoding)
            )
            
            if cosine_sim >= (1 - threshold):
                return self._row_to_employee(row)
        return None

    def get_all_employees(self) -> list[Employee]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM employees")
        return [self._row_to_employee(row) for row in cursor.fetchall()]

    def update_employee(self, emp_id: int, full_name: Optional[str] = None, position: Optional[str] = None, 
                        face_encoding: Optional[bytes] = None, photo_path: Optional[str] = None):
        cursor = self._conn.cursor()
        updates = []
        params = []
        if full_name:
            updates.append("full_name = ?")
            params.append(full_name)
        if position:
            updates.append("position = ?")
            params.append(position)
        if face_encoding:
            updates.append("face_encoding = ?")
            params.append(face_encoding)
        if photo_path:
            updates.append("photo_path = ?")
            params.append(photo_path)
        
        if updates:
            params.append(emp_id)
            cursor.execute(f"UPDATE employees SET {', '.join(updates)} WHERE id = ?", params)
            self._conn.commit()

    def delete_employee(self, emp_id: int):
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
        self._conn.commit()

    def get_key(self, cabinet: str) -> Optional[dict]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM keys WHERE cabinet = ?", (cabinet,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_keys(self) -> list[dict]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM keys")
        return [dict(row) for row in cursor.fetchall()]

    def add_key(self, cabinet: str):
        cursor = self._conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO keys (cabinet, status) VALUES (?, 'AVAILABLE')", (cabinet,))
        self._conn.commit()

    def update_key(self, cabinet: str, status: str, holder_id: Optional[int] = None, holder_name: Optional[str] = None):
        cursor = self._conn.cursor()
        if holder_id is None:
            cursor.execute("UPDATE keys SET status = ?, holder_id = NULL, holder_name = NULL WHERE cabinet = ?", 
                          (status, cabinet))
        else:
            cursor.execute("UPDATE keys SET status = ?, holder_id = ?, holder_name = ? WHERE cabinet = ?",
                          (status, holder_id, holder_name, cabinet))
        self._conn.commit()

    def delete_key(self, cabinet: str):
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM keys WHERE cabinet = ?", (cabinet,))
        self._conn.commit()

    def _row_to_employee(self, row: sqlite3.Row) -> Employee:
        return Employee(
            id=row["id"],
            name=row["full_name"],
            position=row["position"],
            face_encoding=row["face_encoding"],
            photo_path=row["photo_path"]
        )

    def close(self):
        if self._conn:
            self._conn.close()
