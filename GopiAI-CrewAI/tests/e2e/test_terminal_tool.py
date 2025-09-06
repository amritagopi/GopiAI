import os
import sys
import pathlib
import pytest

from path_manager import setup_project_paths
from tools.gopiai_integration.terminal_tool import TerminalTool

# Ensure project root on path
ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    # Инициализируем пути проекта
    path_manager = setup_project_paths()


def test_terminal_tool_pwd_unsafe_mode(tmp_path, monkeypatch):
    # Enable unsafe mode for this test process
    monkeypatch.setenv("GOPIAI_TERMINAL_UNSAFE", "1")

    tool = TerminalTool()
    # On Windows 'pwd' is a bash builtin; use 'cd' or 'echo %cd%'. We'll use Python to be cross-platform.
    # But since tool executes via shell=True, we handle Windows separately.
    if os.name == 'nt':
        cmd = "cd"
    else:
        cmd = "pwd"

    res = tool._run(cmd)
    assert isinstance(res, dict)
    out = res.get("terminal_output", {})
    assert out.get("success") is True, f"Command failed: {out}"
    output = out.get("output", "").strip()
    # On Windows, 'cd' prints current dir; on *nix, pwd prints it.
    assert output, f"Empty output for command {cmd}"
    # Sanity: output should be an existing directory
    assert pathlib.Path(output).exists(), f"Path does not exist: {output}"


@pytest.mark.skipif(os.name != 'nt', reason="Windows-only echo test")
def test_terminal_tool_echo_windows(monkeypatch):
    monkeypatch.setenv("GOPIAI_TERMINAL_UNSAFE", "1")
    tool = TerminalTool()
    res = tool._run("echo hello")
    out = res.get("terminal_output", {})
    assert out.get("success") is True
    assert "hello" in (out.get("output") or "")