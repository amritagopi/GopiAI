#!/usr/bin/env python
"""
Script to set up MCP servers for GopiAI.
This script reads the mcp.json configuration and installs the required NPM packages.
"""

import json
import os
import subprocess
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


def install_npm_packages(packages: List[str]) -> None:
    """Install NPM packages globally."""
    if not packages:
        print("No packages to install")
        return

    install_cmd = ["npm", "install", "-g"] + packages
    print(f"Running: {' '.join(install_cmd)}")

    try:
        result = subprocess.run(
            install_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error installing npm packages: {e}")
        print(e.stderr)
        # Don't exit, try to continue with remaining steps


def create_data_directory() -> None:
    """Create data directory if it doesn't exist."""
    config = load_config()
    if "database" in config and "path" in config["database"]:
        db_path = config["database"]["path"]
        db_dir = os.path.dirname(db_path)

        if db_dir and not os.path.exists(db_dir):
            print(f"Creating data directory: {db_dir}")
            os.makedirs(db_dir)


def main() -> None:
    """Main entry point."""
    print("Setting up MCP servers for GopiAI...")

    config = load_config()

    if "servers" in config:
        # Extract package names from server configurations
        packages = [server["package"] for server in config["servers"] if "package" in server]

        # Install NPM packages
        install_npm_packages(packages)
    else:
        print("No server configurations found in mcp.json")

    # Create data directory for SQLite
    create_data_directory()

    print("MCP server setup completed!")


if __name__ == "__main__":
    main()
