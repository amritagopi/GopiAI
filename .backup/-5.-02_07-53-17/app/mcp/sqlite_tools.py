import json
import os
import sqlite3
from typing import Any, Dict, List, Optional, Union

from app.logger import logger


class SQLiteDatabase:
    """SQLite database manager for GopiAI."""

    def __init__(self, db_path: str = "data/gopi_ai.db"):
        """Initialize SQLite database connection."""
        self.db_path = db_path
        self._ensure_db_directory()
        self.conn = None
        self.cursor = None

    def _ensure_db_directory(self) -> None:
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def connect(self) -> None:
        """Connect to the SQLite database."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to SQLite database: {self.db_path}")

    def close(self) -> None:
        """Close the SQLite database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            logger.info("Closed SQLite database connection")

    def execute(self, query: str, params: Optional[tuple] = None) -> None:
        """Execute an SQL query."""
        self.connect()
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            raise

    def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a query and fetch all results."""
        self.connect()
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            raise

    def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Execute a query and fetch one result."""
        self.connect()
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            raise

    def create_table(self, table_name: str, columns: List[str]) -> None:
        """Create a table with specified columns."""
        columns_str = ", ".join(columns)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        self.execute(query)
        logger.info(f"Created table: {table_name}")

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        """Insert data into a table."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.execute(query, tuple(data.values()))
        return self.cursor.lastrowid

    def update(self, table_name: str, data: Dict[str, Any], condition: str, params: tuple) -> int:
        """Update data in a table."""
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        params_full = tuple(data.values()) + params
        self.execute(query, params_full)
        return self.cursor.rowcount

    def delete(self, table_name: str, condition: str, params: tuple) -> int:
        """Delete data from a table."""
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.execute(query, params)
        return self.cursor.rowcount


# Initialize global database instance
db = SQLiteDatabase()


# MCP tool functions
async def init_database(db_path: Optional[str] = None) -> str:
    """
    Initialize the SQLite database with required tables.

    Args:
        db_path: Optional custom path to the database

    Returns:
        Status message
    """
    try:
        # Load table definitions from mcp.json
        with open("mcp.json", "r") as f:
            config = json.load(f)

        if db_path:
            db.db_path = db_path
        elif "database" in config and "path" in config["database"]:
            db.db_path = config["database"]["path"]

        db.connect()

        # Create tables defined in the config
        if "database" in config and "init_tables" in config["database"]:
            for table_def in config["database"]["init_tables"]:
                table_name = table_def["name"]
                columns = table_def["columns"]
                db.create_table(table_name, columns)

        return json.dumps({"status": "success", "message": f"Database initialized at {db.db_path}"})
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return json.dumps({"status": "error", "message": str(e)})


async def execute_query(query: str, params: Optional[str] = None) -> str:
    """
    Execute a raw SQL query.

    Args:
        query: SQL query to execute
        params: JSON string of parameters (optional)

    Returns:
        Status message
    """
    try:
        params_tuple = tuple(json.loads(params)) if params else None
        db.execute(query, params_tuple)
        return json.dumps({"status": "success", "affected_rows": db.cursor.rowcount})
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return json.dumps({"status": "error", "message": str(e)})


async def select_query(query: str, params: Optional[str] = None, one: bool = False) -> str:
    """
    Execute a SELECT query and return results.

    Args:
        query: SELECT query to execute
        params: JSON string of parameters (optional)
        one: Whether to return only one result

    Returns:
        JSON string of results
    """
    try:
        params_tuple = tuple(json.loads(params)) if params else None
        if one:
            result = db.fetch_one(query, params_tuple)
            return json.dumps({"status": "success", "data": result})
        else:
            results = db.fetch_all(query, params_tuple)
            return json.dumps({"status": "success", "data": results})
    except Exception as e:
        logger.error(f"Error executing select query: {e}")
        return json.dumps({"status": "error", "message": str(e)})


async def insert_data(table: str, data: str) -> str:
    """
    Insert data into a table.

    Args:
        table: Table name
        data: JSON string of data to insert

    Returns:
        Status message with inserted ID
    """
    try:
        data_dict = json.loads(data)
        last_id = db.insert(table, data_dict)
        return json.dumps({"status": "success", "id": last_id})
    except Exception as e:
        logger.error(f"Error inserting data: {e}")
        return json.dumps({"status": "error", "message": str(e)})


async def update_data(table: str, data: str, condition: str, params: str) -> str:
    """
    Update data in a table.

    Args:
        table: Table name
        data: JSON string of data to update
        condition: WHERE condition
        params: JSON string of parameters for condition

    Returns:
        Status message with count of affected rows
    """
    try:
        data_dict = json.loads(data)
        params_tuple = tuple(json.loads(params))
        affected = db.update(table, data_dict, condition, params_tuple)
        return json.dumps({"status": "success", "affected_rows": affected})
    except Exception as e:
        logger.error(f"Error updating data: {e}")
        return json.dumps({"status": "error", "message": str(e)})


async def delete_data(table: str, condition: str, params: str) -> str:
    """
    Delete data from a table.

    Args:
        table: Table name
        condition: WHERE condition
        params: JSON string of parameters for condition

    Returns:
        Status message with count of deleted rows
    """
    try:
        params_tuple = tuple(json.loads(params))
        affected = db.delete(table, condition, params_tuple)
        return json.dumps({"status": "success", "deleted_rows": affected})
    except Exception as e:
        logger.error(f"Error deleting data: {e}")
        return json.dumps({"status": "error", "message": str(e)})


async def create_table(table: str, columns: List[str]) -> str:
    """
    Create a new table.

    Args:
        table: Table name
        columns: List of column definitions

    Returns:
        Status message
    """
    try:
        db.create_table(table, columns)
        return json.dumps({"status": "success", "message": f"Table {table} created"})
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        return json.dumps({"status": "error", "message": str(e)})
