import json
import os
from typing import Dict, List, Optional, Any

from app.logger import logger


class SerenaTools:
    """Tools for Serena integration in GopiAI."""

    @staticmethod
    async def restart_language_server(random_string: str = "") -> str:
        """
        Restart the language server for Serena integration.

        Args:
            random_string: Dummy parameter for no-parameter tools

        Returns:
            Status message
        """
        try:
            logger.info("Restarting language server for Serena")
            # Здесь был бы код для перезапуска языкового сервера
            return json.dumps({"status": "success", "message": "Language server restarted"})
        except Exception as e:
            logger.error(f"Error restarting language server: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    @staticmethod
    async def read_file(
        relative_path: str,
        start_line: int = 0,
        end_line: Optional[int] = None,
        max_answer_chars: int = 200000
    ) -> str:
        """
        Read the given file or a chunk of it.

        Args:
            relative_path: The relative path to the file to read
            start_line: The 0-based index of the first line to be retrieved
            end_line: The 0-based index of the last line to be retrieved (inclusive)
            max_answer_chars: Max characters to return

        Returns:
            File content
        """
        try:
            if not os.path.exists(relative_path):
                return json.dumps({"status": "error", "message": f"File not found: {relative_path}"})

            with open(relative_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            if end_line is None:
                end_line = len(lines) - 1

            # Ensure bounds
            start_line = max(0, min(start_line, len(lines) - 1))
            end_line = max(start_line, min(end_line, len(lines) - 1))

            content = "".join(lines[start_line:end_line+1])

            # Check if content is too large
            if len(content) > max_answer_chars:
                return json.dumps({
                    "status": "error",
                    "message": f"Content too large ({len(content)} chars). Reduce range or increase max_answer_chars."
                })

            return json.dumps({
                "status": "success",
                "content": content,
                "start_line": start_line,
                "end_line": end_line,
                "total_lines": len(lines)
            })
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    @staticmethod
    async def create_text_file(relative_path: str, content: str) -> str:
        """
        Write a new file or overwrite an existing file.

        Args:
            relative_path: The relative path to the file to create
            content: The content to write to the file

        Returns:
            Status message
        """
        try:
            # Ensure directory exists
            directory = os.path.dirname(relative_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            with open(relative_path, "w", encoding="utf-8") as file:
                file.write(content)

            return json.dumps({
                "status": "success",
                "message": f"File created/updated: {relative_path}",
                "path": relative_path
            })
        except Exception as e:
            logger.error(f"Error creating text file: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    @staticmethod
    async def list_dir(relative_path: str, recursive: bool = False, max_answer_chars: int = 200000) -> str:
        """
        Lists files and directories in the given directory.

        Args:
            relative_path: The relative path to the directory to list
            recursive: Whether to scan subdirectories recursively
            max_answer_chars: Max characters in output

        Returns:
            JSON object with directories and files
        """
        try:
            if not os.path.exists(relative_path):
                return json.dumps({"status": "error", "message": f"Directory not found: {relative_path}"})

            if not os.path.isdir(relative_path):
                return json.dumps({"status": "error", "message": f"Not a directory: {relative_path}"})

            result = {"directories": [], "files": []}

            if recursive:
                for root, dirs, files in os.walk(relative_path):
                    # Make paths relative to the requested path
                    rel_root = os.path.relpath(root, relative_path)
                    if rel_root == ".":
                        rel_root = ""

                    for dir_name in dirs:
                        dir_path = os.path.join(rel_root, dir_name) if rel_root else dir_name
                        result["directories"].append(dir_path)

                    for file_name in files:
                        file_path = os.path.join(rel_root, file_name) if rel_root else file_name
                        result["files"].append(file_path)
            else:
                # Non-recursive listing
                with os.scandir(relative_path) as entries:
                    for entry in entries:
                        if entry.is_dir():
                            result["directories"].append(entry.name)
                        else:
                            result["files"].append(entry.name)

            # Sort results for better readability
            result["directories"].sort()
            result["files"].sort()

            json_result = json.dumps(result)
            if len(json_result) > max_answer_chars:
                return json.dumps({
                    "status": "error",
                    "message": f"Output too large ({len(json_result)} chars). Use a smaller directory or disable recursion."
                })

            return json_result
        except Exception as e:
            logger.error(f"Error listing directory: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    @staticmethod
    async def get_symbols_overview(relative_path: str, max_answer_chars: int = 200000) -> str:
        """
        Gets an overview of the given file or directory.

        Args:
            relative_path: The path to analyze
            max_answer_chars: Max characters in output

        Returns:
            Symbol overview
        """
        try:
            # Базовая заглушка - в реальной реализации нужен более сложный парсинг кода
            # Здесь мы просто эмулируем информацию о символах
            if not os.path.exists(relative_path):
                return json.dumps({"status": "error", "message": f"Path not found: {relative_path}"})

            result = {}

            if os.path.isdir(relative_path):
                # Находим все Python файлы в директории
                for root, _, files in os.walk(relative_path):
                    for file in files:
                        if file.endswith(".py"):
                            file_path = os.path.join(root, file)
                            rel_file_path = os.path.relpath(file_path, relative_path)
                            result[rel_file_path] = SerenaTools._extract_symbols(file_path)
            else:
                # Анализируем один файл
                if relative_path.endswith(".py"):
                    result[os.path.basename(relative_path)] = SerenaTools._extract_symbols(relative_path)
                else:
                    return json.dumps({"status": "error", "message": "Only Python files are supported for symbol extraction"})

            json_result = json.dumps(result)
            if len(json_result) > max_answer_chars:
                return json.dumps({
                    "status": "error",
                    "message": f"Output too large ({len(json_result)} chars). Use a smaller file or directory."
                })

            return json_result
        except Exception as e:
            logger.error(f"Error getting symbols overview: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    @staticmethod
    def _extract_symbols(file_path: str) -> List[Dict[str, Any]]:
        """
        Extract symbols from a Python file (simplified version).

        This is a placeholder for actual symbol extraction logic that would use
        a proper AST parser or language server.
        """
        symbols = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            current_line = 0
            for line in lines:
                current_line += 1
                line = line.strip()

                # Очень простой анализ для демонстрационных целей
                if line.startswith("class "):
                    class_name = line.split("class ")[1].split("(")[0].split(":")[0].strip()
                    symbols.append({
                        "name": class_name,
                        "kind": 5,  # class
                        "line": current_line - 1,
                        "column": line.index("class "),
                    })
                elif line.startswith("def "):
                    func_name = line.split("def ")[1].split("(")[0].strip()
                    symbols.append({
                        "name": func_name,
                        "kind": 12,  # function
                        "line": current_line - 1,
                        "column": line.index("def "),
                    })
                elif " = " in line and not line.startswith((" ", "#", "'")):
                    var_name = line.split(" = ")[0].strip()
                    if var_name.isupper():
                        kind = 14  # constant
                    else:
                        kind = 13  # variable
                    symbols.append({
                        "name": var_name,
                        "kind": kind,
                        "line": current_line - 1,
                        "column": 0,
                    })

            return symbols
        except Exception as e:
            logger.error(f"Error extracting symbols from {file_path}: {e}")
            return []


# Экспорт функций для MCP
restart_language_server = SerenaTools.restart_language_server
read_file = SerenaTools.read_file
create_text_file = SerenaTools.create_text_file
list_dir = SerenaTools.list_dir
get_symbols_overview = SerenaTools.get_symbols_overview
