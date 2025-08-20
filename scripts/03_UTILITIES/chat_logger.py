import sys
import re
import datetime

def clean_line(line):
    # Удаляем управляющие символы и ANSI-коды
    line = re.sub(r'\x1b\[[0-9;]*m', '', line)  # ANSI escape codes
    line = re.sub(r'\x07', '', line)  # Bell character
    line = re.sub(r'\r', '', line)   # Carriage return
    return line

def main():
    log_path = "C:/Users/crazy/.gemini/chat_history/chat_history.md"
    
    # Добавляем метку времени для новой сессии
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"--- Session started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")

    buffer = ""
    while True:
        line = sys.stdin.readline()
        if not line:
            break

        line = clean_line(line.strip())

        if line.startswith("user:"):
            if buffer:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(buffer + "\n")
                buffer = ""
            buffer += line + "\n"
        elif line.startswith("model:"):
            if buffer:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(buffer + "\n")
                buffer = ""
            buffer += line + "\n"
        elif line.startswith("--- Session started:"):
            if buffer:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(buffer + "\n")
                buffer = ""
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        elif line.strip() == "":
            if buffer:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(buffer + "\n")
                buffer = ""
        else:
            buffer += line + "\n"

    if buffer:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(buffer + "\n")

if __name__ == "__main__":
    main()
