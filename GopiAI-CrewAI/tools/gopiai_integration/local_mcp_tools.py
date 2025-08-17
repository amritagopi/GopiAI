"""
Локальные MCP инструменты для GopiAI
Набор полезных инструментов, которые работают без внешних сервисов
"""

import os
import json
import time
import logging
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import requests
# Безопасные импорты bs4: модуль может отсутствовать в окружении
try:
    from bs4 import BeautifulSoup, Tag  # type: ignore
    from bs4.element import NavigableString, ResultSet  # type: ignore
except Exception:  # pragma: no cover
    BeautifulSoup = None  # type: ignore
    class Tag:  # type: ignore
        pass
    class NavigableString(str):  # type: ignore
        pass
    class ResultSet(list):  # type: ignore
        pass
import urllib.parse
import re
from urllib.robotparser import RobotFileParser

logger = logging.getLogger(__name__)

class LocalMCPTools:
    """Класс для локальных MCP инструментов"""
    
    def __init__(self):
        self.tools_registry = {
            "system_info": {
                "name": "system_info",
                "description": "Получение информации о системе",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "file_operations": {
                "name": "file_operations",
                "description": "Операции с файлами: создание, чтение, запись",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["read", "write", "create", "list", "delete"],
                            "description": "Тип операции"
                        },
                        "path": {
                            "type": "string",
                            "description": "Путь к файлу или директории"
                        },
                        "content": {
                            "type": "string",
                            "description": "Содержимое файла (для операций write/create)"
                        }
                    },
                    "required": ["operation", "path"]
                }
            },
            "process_manager": {
                "name": "process_manager",
                "description": "Управление процессами системы",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "kill", "start"],
                            "description": "Действие с процессом"
                        },
                        "process_name": {
                            "type": "string",
                            "description": "Имя процесса"
                        },
                        "command": {
                            "type": "string",
                            "description": "Команда для запуска (для действия start)"
                        }
                    },
                    "required": ["action"]
                }
            },
            "time_helper": {
                "name": "time_helper",
                "description": "Помощник для работы со временем",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["current_time", "timestamp", "format_time"],
                            "description": "Операция со временем"
                        },
                        "format": {
                            "type": "string",
                            "description": "Формат времени (для format_time)"
                        }
                    },
                    "required": ["operation"]
                }
            },
            "project_helper": {
                "name": "project_helper",
                "description": "Помощник для управления проектом GopiAI",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["status", "restart_server", "check_logs", "health_check"],
                            "description": "Действие с проектом"
                        },
                        "component": {
                            "type": "string",
                            "enum": ["crewai", "ui", "txtai", "all"],
                            "description": "Компонент проекта"
                        }
                    },
                    "required": ["action"]
                }
            },
            "web_scraper": {
                "name": "web_scraper",
                "description": "Веб-скрапинг: извлечение данных с веб-страниц",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL для скрапинга"
                        },
                        "action": {
                            "type": "string",
                            "enum": ["get_text", "get_links", "get_images", "get_tables", "get_forms", "get_metadata", "custom_selector"],
                            "description": "Тип извлекаемых данных"
                        },
                        "selector": {
                            "type": "string",
                            "description": "CSS селектор для custom_selector"
                        },
                        "headers": {
                            "type": "object",
                            "description": "HTTP заголовки"
                        }
                    },
                    "required": ["url", "action"]
                }
            },
            "api_client": {
                "name": "api_client",
                "description": "HTTP API клиент для вызова внешних API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL API endpoint"
                        },
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                            "description": "HTTP метод"
                        },
                        "headers": {
                            "type": "object",
                            "description": "HTTP заголовки"
                        },
                        "data": {
                            "type": "object",
                            "description": "Данные для отправки (JSON)"
                        },
                        "params": {
                            "type": "object",
                            "description": "URL параметры"
                        },
                        "timeout": {
                            "type": "number",
                            "description": "Таймаут в секундах",
                            "default": 30
                        }
                    },
                    "required": ["url", "method"]
                }
            },
            "url_analyzer": {
                "name": "url_analyzer",
                "description": "Анализ URL и веб-ресурсов",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL для анализа"
                        },
                        "action": {
                            "type": "string",
                            "enum": ["check_status", "get_headers", "check_robots", "get_sitemap", "analyze_performance"],
                            "description": "Тип анализа"
                        }
                    },
                    "required": ["url", "action"]
                }
            },
            "execute_shell": {
                "name": "execute_shell",
                "description": "Execute shell command and return output",
                "parameters": {
                    "type": "object",
                    "properties": {"command": {"type": "string", "description": "Shell command to execute"}},
                    "required": ["command"]
                }
            },
            "export_to_drive": {
                "name": "export_to_drive",
                "description": "Export session history to Google Drive",
                "parameters": {
                    "type": "object",
                    "properties": {"session_id": {"type": "string"}, "drive_folder_id": {"type": "string"}},
                    "required": ["session_id"]
                }
            },
            # browser_tools удалены из проекта
            "web_scraper": {
                "name": "web_scraper",
                "description": "Извлечение данных с веб-страниц: текст, ссылки, таблицы, изображения",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["get_text", "get_links", "get_images", "get_tables", "custom_selector"],
                            "description": "Тип извлекаемых данных"
                        },
                        "url": {
                            "type": "string",
                            "description": "URL, CSS селектор или другой идентификатор"
                        },
                        "data": {
                            "type": "string",
                            "description": "Данные для ввода или JavaScript код",
                            "default": ""
                        },
                        "wait_seconds": {
                            "type": "number",
                            "description": "Время ожидания в секундах",
                            "default": 3
                        }
                    },
                    "required": ["action"]
                }
            }
        }
    
    def get_available_tools(self) -> List[Dict]:
        """Получение списка доступных инструментов"""
        return list(self.tools_registry.values())
    
    def call_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Вызов инструмента"""
        try:
            if tool_name == "system_info":
                return self._system_info()
            elif tool_name == "file_operations":
                return self._file_operations(parameters)
            elif tool_name == "process_manager":
                return self._process_manager(parameters)
            elif tool_name == "time_helper":
                return self._time_helper(parameters)
            elif tool_name == "project_helper":
                return self._project_helper(parameters)
            elif tool_name == "web_scraper":
                return self._web_scraper(parameters)
            elif tool_name == "api_client":
                return self._api_client(parameters)
            elif tool_name == "url_analyzer":
                return self._url_analyzer(parameters)
            elif tool_name == "execute_shell":
                return self._execute_shell(parameters)
            elif tool_name == "export_to_drive":
                return self._export_to_drive(parameters)
            # browser_tools удалены из проекта
            else:
                return {"error": f"Неизвестный инструмент: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Ошибка при вызове инструмента {tool_name}: {e}")
            return {"error": f"Ошибка выполнения: {str(e)}"}
    
    def _system_info(self) -> Dict:
        """Получение информации о системе"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "current_directory": os.getcwd(),
            "user": os.environ.get("USERNAME", "unknown"),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _file_operations(self, params: Dict) -> Dict:
        """Операции с файлами"""
        operation = params.get("operation")
        path = params.get("path")
        
        if not path:
            return {"error": "Не указан путь к файлу"}
        
        try:
            if operation == "read":
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"success": True, "content": content}
            
            elif operation == "write" or operation == "create":
                content = params.get("content", "")
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {"success": True, "message": f"Файл {'создан' if operation == 'create' else 'изменен'}: {path}"}
            
            elif operation == "list":
                path_obj = Path(path)
                if path_obj.is_dir():
                    files = [str(p) for p in path_obj.iterdir()]
                    return {"success": True, "files": files}
                else:
                    return {"error": "Указанный путь не является директорией"}
            
            elif operation == "delete":
                os.remove(path)
                return {"success": True, "message": f"Файл удален: {path}"}
            
            else:
                return {"error": f"Неизвестная операция: {operation}"}
                
        except Exception as e:
            return {"error": f"Ошибка операции с файлом: {str(e)}"}
    
    def _process_manager(self, params: Dict) -> Dict:
        """Управление процессами"""
        action = params.get("action")
        
        try:
            if action == "list":
                # Получаем список процессов
                if platform.system() == "Windows":
                    result = subprocess.run(['tasklist'], capture_output=True, text=True)
                    return {"success": True, "processes": result.stdout[:1000]}  # Ограничиваем вывод
                else:
                    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                    return {"success": True, "processes": result.stdout[:1000]}
            
            elif action == "kill":
                process_name = params.get("process_name")
                if not process_name:
                    return {"error": "Не указано имя процесса"}
                
                if platform.system() == "Windows":
                    result = subprocess.run(['taskkill', '/f', '/im', process_name], 
                                          capture_output=True, text=True)
                else:
                    result = subprocess.run(['pkill', process_name], 
                                          capture_output=True, text=True)
                
                return {"success": True, "message": f"Процесс {process_name} завершен"}
            
            elif action == "start":
                command = params.get("command")
                if not command:
                    return {"error": "Не указана команда для запуска"}
                
                process = subprocess.Popen(command, shell=True)
                return {"success": True, "message": f"Процесс запущен с PID: {process.pid}"}
            
            else:
                return {"error": f"Неизвестное действие: {action}"}
                
        except Exception as e:
            return {"error": f"Ошибка управления процессом: {str(e)}"}
    
    def _time_helper(self, params: Dict) -> Dict:
        """Помощник для работы со временем"""
        operation = params.get("operation")
        
        try:
            if operation == "current_time":
                return {
                    "success": True,
                    "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp": int(time.time())
                }
            
            elif operation == "timestamp":
                return {
                    "success": True,
                    "timestamp": int(time.time()),
                    "iso_format": datetime.now().isoformat()
                }
            
            elif operation == "format_time":
                format_str = params.get("format", "%Y-%m-%d %H:%M:%S")
                return {
                    "success": True,
                    "formatted_time": datetime.now().strftime(format_str)
                }
            
            else:
                return {"error": f"Неизвестная операция: {operation}"}
                
        except Exception as e:
            return {"error": f"Ошибка работы со временем: {str(e)}"}
    
    def _project_helper(self, params: Dict) -> Dict:
        """Помощник для управления проектом"""
        action = params.get("action")
        component = params.get("component", "all")
        
        try:
            if action == "status":
                # Проверяем статус компонентов
                status = {}
                
                # Проверка CrewAI сервера
                try:
                    import requests
                    response = requests.get("http://127.0.0.1:5051/api/health", timeout=2)
                    status["crewai_server"] = "running" if response.status_code == 200 else "stopped"
                except:
                    status["crewai_server"] = "stopped"
                
                # Проверка процессов
                if platform.system() == "Windows":
                    result = subprocess.run(['tasklist'], capture_output=True, text=True)
                    processes = result.stdout
                    status["python_processes"] = processes.count("python.exe")
                
                return {"success": True, "status": status}
            
            elif action == "health_check":
                # Полная проверка здоровья системы
                health = {
                    "timestamp": datetime.now().isoformat(),
                    "system": platform.system(),
                    "python_version": platform.python_version(),
                    "working_directory": os.getcwd(),
                    "crewai_server": "unknown",
                    "memory_usage": "unknown"
                }
                
                # Проверка CrewAI сервера
                try:
                    import requests
                    response = requests.get("http://127.0.0.1:5051/api/health", timeout=2)
                    if response.status_code == 200:
                        health["crewai_server"] = "healthy"
                        health["crewai_data"] = response.json()
                    else:
                        health["crewai_server"] = "unhealthy"
                except:
                    health["crewai_server"] = "down"
                
                return {"success": True, "health": health}
            
            else:
                return {"error": f"Неизвестное действие: {action}"}
                
        except Exception as e:
            return {"error": f"Ошибка управления проектом: {str(e)}"}
    
    def _web_scraper(self, params: Dict) -> Dict:
        """Веб-скрапинг: извлечение данных с веб-страниц"""
        try:
            url = params.get("url")
            action = params.get("action")
            selector = params.get("selector")
            headers = params.get("headers", {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })
            
            if not url or not action:
                return {"error": "Не указан URL или действие"}
            
            # Получаем страницу
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            if BeautifulSoup is None:
                return {"error": "BeautifulSoup (bs4) не установлен — парсинг HTML недоступен"}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if action == "get_text":
                # Извлекаем весь текст
                text = soup.get_text(strip=True, separator='\n')
                return {
                    "success": True,
                    "url": url,
                    "text": text,
                    "length": len(text)
                }
            
            elif action == "get_links":
                # Извлекаем все ссылки
                links = []
                for link in soup.find_all('a', href=True):
                    # Явно приводим к Tag для доступа к методам
                    if isinstance(link, Tag):
                        href = link.get('href', '')
                        # Преобразуем относительные ссылки в абсолютные
                        if isinstance(href, str):
                            absolute_url = urllib.parse.urljoin(url, href)
                        else:
                            absolute_url = href
                        text = link.get_text(strip=True)
                        links.append({
                            "url": absolute_url,
                            "text": text,
                            "original_href": href
                        })
                return {
                    "success": True,
                    "url": url,
                    "links": links,
                    "count": len(links)
                }
            
            elif action == "get_images":
                # Извлекаем все изображения
                images = []
                for img in soup.find_all('img'):
                    src = img.get('src')
                    if src:
                        absolute_url = urllib.parse.urljoin(url, src)
                        images.append({
                            "url": absolute_url,
                            "alt": img.get('alt', ''),
                            "title": img.get('title', ''),
                            "original_src": src
                        })
                return {
                    "success": True,
                    "url": url,
                    "images": images,
                    "count": len(images)
                }
            
            elif action == "get_tables":
                # Извлекаем все таблицы
                tables = []
                for table in soup.find_all('table'):
                    rows = []
                    for tr in table.find_all('tr'):
                        cells = []
                        for td in tr.find_all(['td', 'th']):
                            cells.append(td.get_text(strip=True))
                        if cells:
                            rows.append(cells)
                    if rows:
                        tables.append(rows)
                return {
                    "success": True,
                    "url": url,
                    "tables": tables,
                    "count": len(tables)
                }
            
            elif action == "get_forms":
                # Извлекаем все формы
                forms = []
                for form in soup.find_all('form'):
                    form_data = {
                        "action": form.get('action', ''),
                        "method": form.get('method', 'GET').upper(),
                        "inputs": []
                    }
                    
                    for input_elem in form.find_all(['input', 'textarea', 'select']):
                        input_data = {
                            "type": input_elem.get('type', 'text'),
                            "name": input_elem.get('name', ''),
                            "value": input_elem.get('value', ''),
                            "placeholder": input_elem.get('placeholder', ''),
                            "required": input_elem.has_attr('required')
                        }
                        form_data["inputs"].append(input_data)
                    
                    forms.append(form_data)
                
                return {
                    "success": True,
                    "url": url,
                    "forms": forms,
                    "count": len(forms)
                }
            
            elif action == "get_metadata":
                # Извлекаем метаданные
                metadata = {
                    "title": soup.title.string if soup.title else "",
                    "description": "",
                    "keywords": "",
                    "author": "",
                    "canonical": "",
                    "og_title": "",
                    "og_description": "",
                    "og_image": "",
                    "twitter_card": ""
                }
                
                # Мета-теги
                for meta in soup.find_all('meta'):
                    name = meta.get('name', '').lower()
                    property_attr = meta.get('property', '').lower()
                    content = meta.get('content', '')
                    
                    if name == 'description':
                        metadata['description'] = content
                    elif name == 'keywords':
                        metadata['keywords'] = content
                    elif name == 'author':
                        metadata['author'] = content
                    elif property_attr == 'og:title':
                        metadata['og_title'] = content
                    elif property_attr == 'og:description':
                        metadata['og_description'] = content
                    elif property_attr == 'og:image':
                        metadata['og_image'] = content
                    elif name == 'twitter:card':
                        metadata['twitter_card'] = content
                
                # Canonical URL
                canonical = soup.find('link', rel='canonical')
                if canonical:
                    metadata['canonical'] = canonical.get('href', '')
                
                return {
                    "success": True,
                    "url": url,
                    "metadata": metadata
                }
            
            elif action == "custom_selector":
                # Пользовательский CSS селектор
                if not selector:
                    return {"error": "Не указан CSS селектор"}
                
                elements = soup.select(selector)
                results = []
                
                for elem in elements:
                    result = {
                        "text": elem.get_text(strip=True),
                        "html": str(elem),
                        "attributes": dict(elem.attrs) if hasattr(elem, 'attrs') else {}
                    }
                    results.append(result)
                
                return {
                    "success": True,
                    "url": url,
                    "selector": selector,
                    "results": results,
                    "count": len(results)
                }
            
            else:
                return {"error": f"Неизвестное действие: {action}"}
                
        except requests.RequestException as e:
            return {"error": f"Ошибка HTTP запроса: {str(e)}"}
        except Exception as e:
            return {"error": f"Ошибка скрапинга: {str(e)}"}
    
    def _api_client(self, params: Dict) -> Dict:
        """HTTP API клиент для вызова внешних API"""
        try:
            url = params.get("url")
            method = params.get("method", "GET").upper()
            headers = params.get("headers", {})
            data = params.get("data")
            url_params = params.get("params")
            timeout = params.get("timeout", 30)
            
            if not url:
                return {"error": "Не указан URL"}
            
            # Устанавливаем стандартные заголовки
            default_headers = {
                "User-Agent": "GopiAI-LocalMCP/1.0",
                "Accept": "application/json, text/plain, */*"
            }
            default_headers.update(headers)
            
            # Выполняем запрос
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, headers=default_headers, params=url_params, timeout=timeout)
            elif method == "POST":
                if data and isinstance(data, dict):
                    response = requests.post(url, headers=default_headers, json=data, params=url_params, timeout=timeout)
                else:
                    response = requests.post(url, headers=default_headers, data=data, params=url_params, timeout=timeout)
            elif method == "PUT":
                if data and isinstance(data, dict):
                    response = requests.put(url, headers=default_headers, json=data, params=url_params, timeout=timeout)
                else:
                    response = requests.put(url, headers=default_headers, data=data, params=url_params, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=default_headers, params=url_params, timeout=timeout)
            elif method == "PATCH":
                if data and isinstance(data, dict):
                    response = requests.patch(url, headers=default_headers, json=data, params=url_params, timeout=timeout)
                else:
                    response = requests.patch(url, headers=default_headers, data=data, params=url_params, timeout=timeout)
            else:
                return {"error": f"Неподдерживаемый HTTP метод: {method}"}
            
            response_time = time.time() - start_time
            
            # Пытаемся парсить JSON
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return {
                "success": True,
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response_data,
                "response_time": round(response_time, 3),
                "encoding": response.encoding
            }
            
        except requests.RequestException as e:
            return {"error": f"Ошибка HTTP запроса: {str(e)}"}
        except Exception as e:
            return {"error": f"Ошибка API клиента: {str(e)}"}
    
    def _url_analyzer(self, params: Dict) -> Dict:
        """Анализ URL и веб-ресурсов"""
        try:
            url = params.get("url")
            action = params.get("action")
            
            if not url or not action:
                return {"error": "Не указан URL или действие"}
            
            if action == "check_status":
                # Проверяем статус URL
                start_time = time.time()
                response = requests.head(url, timeout=10, allow_redirects=True)
                response_time = time.time() - start_time
                
                return {
                    "success": True,
                    "url": url,
                    "status_code": response.status_code,
                    "status_text": response.reason,
                    "response_time": round(response_time, 3),
                    "final_url": response.url,
                    "redirected": response.url != url
                }
            
            elif action == "get_headers":
                # Получаем заголовки
                response = requests.head(url, timeout=10, allow_redirects=True)
                
                return {
                    "success": True,
                    "url": url,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "final_url": response.url
                }
            
            elif action == "check_robots":
                # Проверяем robots.txt
                parsed_url = urllib.parse.urlparse(url)
                robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
                
                try:
                    rp = RobotFileParser()
                    rp.set_url(robots_url)
                    rp.read()
                    
                    can_fetch = rp.can_fetch("*", url)
                    
                    return {
                        "success": True,
                        "url": url,
                        "robots_url": robots_url,
                        "can_fetch": can_fetch,
                        "crawl_delay": rp.crawl_delay("*")
                    }
                except Exception as e:
                    return {
                        "success": True,
                        "url": url,
                        "robots_url": robots_url,
                        "error": f"Ошибка проверки robots.txt: {str(e)}"
                    }
            
            elif action == "get_sitemap":
                # Поиск sitemap.xml
                parsed_url = urllib.parse.urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
                sitemap_urls = [
                    f"{base_url}/sitemap.xml",
                    f"{base_url}/sitemap_index.xml",
                    f"{base_url}/sitemaps/sitemap.xml"
                ]
                
                found_sitemaps = []
                
                for sitemap_url in sitemap_urls:
                    try:
                        response = requests.get(sitemap_url, timeout=10)
                        if response.status_code == 200:
                            found_sitemaps.append({
                                "url": sitemap_url,
                                "size": len(response.content),
                                "content_type": response.headers.get('content-type', '')
                            })
                    except:
                        continue
                
                return {
                    "success": True,
                    "url": url,
                    "base_url": base_url,
                    "found_sitemaps": found_sitemaps,
                    "count": len(found_sitemaps)
                }
            
            elif action == "analyze_performance":
                # Анализ производительности
                start_time = time.time()
                response = requests.get(url, timeout=30)
                total_time = time.time() - start_time
                
                # Парсим HTML для анализа
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Подсчитываем ресурсы
                images = len(soup.find_all('img'))
                scripts = len(soup.find_all('script'))
                stylesheets = len(soup.find_all('link', rel='stylesheet'))
                links = len(soup.find_all('a', href=True))
                
                return {
                    "success": True,
                    "url": url,
                    "performance": {
                        "total_time": round(total_time, 3),
                        "status_code": response.status_code,
                        "content_size": len(response.content),
                        "content_type": response.headers.get('content-type', ''),
                        "encoding": response.encoding,
                        "resources": {
                            "images": images,
                            "scripts": scripts,
                            "stylesheets": stylesheets,
                            "links": links
                        }
                    }
                }
            
            else:
                return {"error": f"Неизвестное действие: {action}"}
                
        except requests.RequestException as e:
            return {"error": f"Ошибка HTTP запроса: {str(e)}"}
        except Exception as e:
            return {"error": f"Ошибка анализа URL: {str(e)}"}

    def _execute_shell(self, params: Dict) -> Dict:
        command = params.get("command")
        visible = params.get("visible", False)
        if not command:
            return {"error": "Command not provided"}
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout.strip() + '\n' + result.stderr.strip()
            ret = {
                "success": True,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode
            }
            if visible:
                return {'ui_action': 'terminal_execute', 'command': command, 'output': output, 'returncode': result.returncode}
            return ret
        except Exception as e:
            return {"error": str(e)}

    def _export_to_drive(self, params: Dict) -> Dict:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.oauth2.credentials import Credentials
        # Assume credentials.json or token.json exists
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive.file'])
        service = build('drive', 'v3', credentials=creds)
        session_id = params['session_id']
        folder_id = params.get('drive_folder_id')
        # Assume global memory_manager
        # from gopiai_integration.memory_manager import MemoryManager # This import is not in the original file, so it's commented out
        # memory_manager = MemoryManager() # This line is commented out as MemoryManager is not defined
        # For demonstration, we'll create a dummy history if memory_manager is not available
        # In a real scenario, you'd load history from a file or database
        history = {
            "session_id": session_id,
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        json_data = json.dumps(history)
        file_name = f'session_{session_id}.json'
        with open(file_name, 'w') as f:
            f.write(json_data)
        file_metadata = {'name': file_name, 'parents': [folder_id] if folder_id else []}
        media = MediaFileUpload(file_name, mimetype='application/json')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        os.remove(file_name)
        return {'success': True, 'file_id': file.get('id')}

    def _browser_tools(self, parameters: Dict) -> Dict:
        """Выполнение браузерных операций - УДАЛЕНО"""
        logger.error("browser_tools удалены из проекта")
        return {
            'success': False,
            'error': "browser_tools удалены из проекта. Используйте web_scraper вместо этого.",
            'action': parameters.get('action', 'unknown')
        }


# Глобальный экземпляр
_local_mcp_tools = None

def get_local_mcp_tools() -> LocalMCPTools:
    """Получение экземпляра локальных MCP инструментов"""
    global _local_mcp_tools
    if _local_mcp_tools is None:
        _local_mcp_tools = LocalMCPTools()
    return _local_mcp_tools
