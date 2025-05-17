#!/usr/bin/env python
"""
Script to initialize the SQLite database for GopiAI.
This script reads the mcp.json configuration and creates the required database and tables.
"""

import json
import os
import sqlite3
import sys
from typing import Dict, List, Any


def load_config() -> Dict[str, Any]:
    """Load MCP configuration from file."""
    config_path = "mcp.json"
    if not os.path.exists(config_path):
        print(f"Error: MCP configuration file not found at {config_path}")
        sys.exit(1)

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading MCP configuration: {e}")
        sys.exit(1)


def ensure_db_directory(db_path: str) -> None:
    """Ensure the database directory exists."""
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        print(f"Creating directory: {db_dir}")
        os.makedirs(db_dir)


def create_tables(db_path: str, table_definitions: List[Dict[str, Any]]) -> None:
    """Create database tables."""
    ensure_db_directory(db_path)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for table_def in table_definitions:
            table_name = table_def["name"]
            columns = table_def["columns"]
            columns_str = ", ".join(columns)

            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
            print(f"Creating table: {table_name}")
            cursor.execute(query)

        conn.commit()
        print(f"Database initialized successfully at: {db_path}")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()


def main() -> None:
    """Main entry point."""
    print("Initializing SQLite database for GopiAI...")

    config = load_config()

    if "database" not in config:
        print("Error: No database configuration found in mcp.json")
        sys.exit(1)

    db_config = config["database"]
    db_path = db_config.get("path", "data/gopi_ai.db")

    if "init_tables" not in db_config:
        print("Error: No table definitions found in mcp.json")
        sys.exit(1)

    table_definitions = db_config["init_tables"]
    create_tables(db_path, table_definitions)

    print("Database initialization completed!")


if __name__ == "__main__":
    main()
