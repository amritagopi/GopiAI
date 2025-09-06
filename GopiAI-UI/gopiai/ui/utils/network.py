
from pathlib import Path

def get_crewai_server_port():
    """
    Читает порт сервера CrewAI из файла ~/.gopiai/crewai_server_port.txt.
    Если файл не найден, возвращает стандартный порт 5051.
    """
    try:
        port_file = Path.home() / ".gopiai" / "crewai_server_port.txt"
        if port_file.exists():
            port_str = port_file.read_text(encoding="utf-8").strip()
            if port_str.isdigit():
                return int(port_str)
    except Exception:
        # В случае любой ошибки, возвращаем стандартный порт
        pass
    return 5051

def get_crewai_server_base_url():
    """
    Возвращает базовый URL сервера CrewAI.
    """
    port = get_crewai_server_port()
    return f"http://127.0.0.1:{port}"
