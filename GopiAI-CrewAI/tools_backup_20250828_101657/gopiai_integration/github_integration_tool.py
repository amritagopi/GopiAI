#!/usr/bin/env python3
"""
🔥 GitHub Integration Tool для GopiAI SmartDelegator
Простая, надежная интеграция с GitHub API без зависимостей от embeddings
"""

import os
import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class GitHubIntegrationTool:
    """
    Простой и надежный GitHub инструмент для GopiAI SmartDelegator
    
    Возможности:
    - Поиск репозиториев
    - Получение информации о репозитории
    - Поиск кода в репозиториях
    - Поиск issues и pull requests
    - Получение информации о пользователе/организации
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Инициализация GitHub инструмента
        
        Args:
            github_token: GitHub Personal Access Token
        """
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        
        if not self.github_token or self.github_token == 'your_github_token_here':
            logger.warning("GitHub токен не найден. Будет использоваться ограниченный доступ к API")
            self.headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'GopiAI-GitHub-Integration/1.0'
            }
        else:
            self.headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'GopiAI-GitHub-Integration/1.0'
            }
        
        self.base_url = 'https://api.github.com'
        logger.info(f"✅ GitHub Integration Tool инициализирован")
    
    def search_repositories(self, query: str, sort: str = 'stars', order: str = 'desc', limit: int = 10) -> Dict[str, Any]:
        """
        Поиск репозиториев на GitHub
        
        Args:
            query: Поисковый запрос
            sort: Сортировка (stars, forks, help-wanted-issues, updated)
            order: Порядок (desc, asc)
            limit: Максимальное количество результатов
            
        Returns:
            Словарь с результатами поиска
        """
        try:
            url = f'{self.base_url}/search/repositories'
            params = {
                'q': query,
                'sort': sort,
                'order': order,
                'per_page': min(limit, 100)  # GitHub API лимит
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for repo in data.get('items', []):
                    results.append({
                        'name': repo['full_name'],
                        'description': repo.get('description', 'Нет описания'),
                        'stars': repo['stargazers_count'],
                        'forks': repo['forks_count'],
                        'language': repo.get('language', 'Unknown'),
                        'url': repo['html_url'],
                        'clone_url': repo['clone_url'],
                        'created_at': repo['created_at'],
                        'updated_at': repo['updated_at'],
                        'topics': repo.get('topics', [])
                    })
                
                return {
                    'success': True,
                    'total_count': data.get('total_count', 0),
                    'results': results,
                    'query': query
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'query': query
                }
                
        except Exception as e:
            logger.error(f"Ошибка поиска репозиториев: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    def get_repository_info(self, repo_name: str) -> Dict[str, Any]:
        """
        Получение подробной информации о репозитории
        
        Args:
            repo_name: Имя репозитория в формате "owner/repo"
            
        Returns:
            Словарь с информацией о репозитории
        """
        try:
            url = f'{self.base_url}/repos/{repo_name}'
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                repo = response.json()
                
                return {
                    'success': True,
                    'name': repo['full_name'],
                    'description': repo.get('description', 'Нет описания'),
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'watchers': repo['watchers_count'],
                    'language': repo.get('language', 'Unknown'),
                    'size': repo['size'],
                    'url': repo['html_url'],
                    'clone_url': repo['clone_url'],
                    'ssh_url': repo['ssh_url'],
                    'created_at': repo['created_at'],
                    'updated_at': repo['updated_at'],
                    'pushed_at': repo['pushed_at'],
                    'topics': repo.get('topics', []),
                    'license': repo.get('license', {}).get('name', 'Unknown') if repo.get('license') else 'Unknown',
                    'default_branch': repo['default_branch'],
                    'open_issues': repo['open_issues_count'],
                    'has_wiki': repo['has_wiki'],
                    'has_pages': repo['has_pages'],
                    'archived': repo['archived'],
                    'disabled': repo['disabled']
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'repo_name': repo_name
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения информации о репозитории: {e}")
            return {
                'success': False,
                'error': str(e),
                'repo_name': repo_name
            }
    
    def search_code(self, query: str, repo: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Поиск кода в репозиториях
        
        Args:
            query: Поисковый запрос
            repo: Конкретный репозиторий для поиска (опционально)
            limit: Максимальное количество результатов
            
        Returns:
            Словарь с результатами поиска кода
        """
        try:
            url = f'{self.base_url}/search/code'
            search_query = query
            
            if repo:
                search_query += f' repo:{repo}'
            
            params = {
                'q': search_query,
                'per_page': min(limit, 100)
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('items', []):
                    results.append({
                        'name': item['name'],
                        'path': item['path'],
                        'repository': item['repository']['full_name'],
                        'url': item['html_url'],
                        'git_url': item['git_url'],
                        'download_url': item.get('download_url'),
                        'score': item['score']
                    })
                
                return {
                    'success': True,
                    'total_count': data.get('total_count', 0),
                    'results': results,
                    'query': query,
                    'repo': repo
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'query': query,
                    'repo': repo
                }
                
        except Exception as e:
            logger.error(f"Ошибка поиска кода: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'repo': repo
            }
    
    def search_issues(self, query: str, repo: Optional[str] = None, state: str = 'open', limit: int = 10) -> Dict[str, Any]:
        """
        Поиск issues и pull requests
        
        Args:
            query: Поисковый запрос
            repo: Конкретный репозиторий для поиска (опционально)
            state: Состояние (open, closed, all)
            limit: Максимальное количество результатов
            
        Returns:
            Словарь с результатами поиска issues
        """
        try:
            url = f'{self.base_url}/search/issues'
            search_query = f'{query} state:{state}'
            
            if repo:
                search_query += f' repo:{repo}'
            
            params = {
                'q': search_query,
                'per_page': min(limit, 100)
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('items', []):
                    results.append({
                        'number': item['number'],
                        'title': item['title'],
                        'body': item.get('body', '')[:200] + '...' if item.get('body') else '',
                        'state': item['state'],
                        'user': item['user']['login'],
                        'repository': item.get('repository_url', '').split('/')[-2:] if item.get('repository_url') else [],
                        'url': item['html_url'],
                        'created_at': item['created_at'],
                        'updated_at': item['updated_at'],
                        'labels': [label['name'] for label in item.get('labels', [])],
                        'is_pull_request': 'pull_request' in item
                    })
                
                return {
                    'success': True,
                    'total_count': data.get('total_count', 0),
                    'results': results,
                    'query': query,
                    'repo': repo,
                    'state': state
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'query': query,
                    'repo': repo,
                    'state': state
                }
                
        except Exception as e:
            logger.error(f"Ошибка поиска issues: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'repo': repo,
                'state': state
            }
    
    def get_user_info(self, username: str) -> Dict[str, Any]:
        """
        Получение информации о пользователе или организации
        
        Args:
            username: Имя пользователя или организации
            
        Returns:
            Словарь с информацией о пользователе
        """
        try:
            url = f'{self.base_url}/users/{username}'
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                user = response.json()
                
                return {
                    'success': True,
                    'login': user['login'],
                    'name': user.get('name', 'Не указано'),
                    'bio': user.get('bio', 'Нет биографии'),
                    'company': user.get('company', 'Не указано'),
                    'location': user.get('location', 'Не указано'),
                    'email': user.get('email', 'Не указано'),
                    'blog': user.get('blog', 'Нет блога'),
                    'twitter': user.get('twitter_username', 'Не указано'),
                    'public_repos': user['public_repos'],
                    'public_gists': user['public_gists'],
                    'followers': user['followers'],
                    'following': user['following'],
                    'created_at': user['created_at'],
                    'updated_at': user['updated_at'],
                    'avatar_url': user['avatar_url'],
                    'html_url': user['html_url'],
                    'type': user['type']  # User или Organization
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'username': username
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения информации о пользователе: {e}")
            return {
                'success': False,
                'error': str(e),
                'username': username
            }
    
    def execute_github_request(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Универсальный метод для выполнения GitHub запросов
        Используется SmartDelegator для вызова конкретных действий
        
        Args:
            action: Тип действия (search_repos, repo_info, search_code, search_issues, user_info)
            params: Параметры для действия
            
        Returns:
            Результат выполнения действия
        """
        try:
            if action == 'search_repos':
                return self.search_repositories(
                    query=params.get('query', ''),
                    sort=params.get('sort', 'stars'),
                    order=params.get('order', 'desc'),
                    limit=params.get('limit', 10)
                )
            
            elif action == 'repo_info':
                return self.get_repository_info(
                    repo_name=params.get('repo_name', '')
                )
            
            elif action == 'search_code':
                return self.search_code(
                    query=params.get('query', ''),
                    repo=params.get('repo'),
                    limit=params.get('limit', 10)
                )
            
            elif action == 'search_issues':
                return self.search_issues(
                    query=params.get('query', ''),
                    repo=params.get('repo'),
                    state=params.get('state', 'open'),
                    limit=params.get('limit', 10)
                )
            
            elif action == 'user_info':
                return self.get_user_info(
                    username=params.get('username', '')
                )
            
            else:
                return {
                    'success': False,
                    'error': f'Неизвестное действие: {action}',
                    'available_actions': ['search_repos', 'repo_info', 'search_code', 'search_issues', 'user_info']
                }
                
        except Exception as e:
            logger.error(f"Ошибка выполнения GitHub запроса: {e}")
            return {
                'success': False,
                'error': str(e),
                'action': action,
                'params': params
            }

# Глобальный экземпляр для использования в SmartDelegator
_github_integration_tool = None

def get_github_integration_tool() -> GitHubIntegrationTool:
    """Возвращает глобальный экземпляр GitHub Integration Tool"""
    global _github_integration_tool
    
    if _github_integration_tool is None:
        _github_integration_tool = GitHubIntegrationTool()
        logger.info("✅ GitHub Integration Tool создан")
    
    return _github_integration_tool

if __name__ == "__main__":
    # Простой тест инструмента
    print("🧪 Тестирование GitHub Integration Tool...")
    
    github_tool = GitHubIntegrationTool()
    
    # Тест поиска репозиториев
    result = github_tool.search_repositories('python AI', limit=3)
    if result['success']:
        print(f"✅ Найдено репозиториев: {result['total_count']}")
        for repo in result['results']:
            print(f"   📦 {repo['name']} ⭐ {repo['stars']}")
    else:
        print(f"❌ Ошибка: {result['error']}")
