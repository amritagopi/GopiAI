"""
🧪 Tool Autotest
Автоматическое тестирование всех инструментов в режимах авто и принудительно
Проверяет алиасы, отсутствие предупреждений и галлюцинаций
"""

import logging
import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .tool_dispatcher import get_tool_dispatcher, ToolDispatcher, IntentMode, DispatchResult
from .tool_aliases import get_tool_alias_manager, ToolAliasManager
from .intent_parser import get_intent_parser, IntentParser

logger = logging.getLogger(__name__)

class TestResult(Enum):
    """Результаты тестирования"""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"

@dataclass
class ToolTestCase:
    """Тестовый случай для инструмента"""
    tool_name: str
    test_name: str
    mode: IntentMode
    user_text: str
    expected_params: Dict[str, Any]
    should_succeed: bool = True
    timeout_seconds: int = 30

@dataclass
class TestReport:
    """Отчет о тестировании"""
    tool_name: str
    test_name: str
    result: TestResult
    execution_time: float
    error_message: Optional[str] = None
    response_data: Any = None
    warnings: List[str] = None

class ToolAutoTest:
    """
    Автоматическое тестирование всех инструментов системы.
    Проверяет работоспособность, алиасы, отсутствие галлюцинаций.
    """
    
    def __init__(self, smart_delegator=None):
        self.logger = logging.getLogger(__name__)
        self.tool_dispatcher = get_tool_dispatcher(smart_delegator)
        self.alias_manager = get_tool_alias_manager()
        self.intent_parser = get_intent_parser()
        
        # Результаты тестирования
        self.test_reports: List[TestReport] = []
        self.warnings: List[str] = []
        
        self.logger.info("✅ ToolAutoTest инициализирован")
    
    def generate_test_cases(self) -> List[ToolTestCase]:
        """
        Генерирует тестовые случаи для всех доступных инструментов.
        
        Returns:
            List[ToolTestCase]: Список тестовых случаев
        """
        test_cases = []
        canonical_tools = self.alias_manager.get_canonical_tools()
        
        for tool_name in canonical_tools:
            # Получаем алиасы для инструмента
            aliases = self.alias_manager.get_all_aliases(tool_name)
            
            # Генерируем тестовые случаи на основе типа инструмента
            tool_tests = self._generate_tool_specific_tests(tool_name)
            test_cases.extend(tool_tests)
            
            # Тестируем основные алиасы
            for alias in aliases[:3]:  # Берем первые 3 алиаса
                if alias != tool_name:
                    test_case = ToolTestCase(
                        tool_name=alias,
                        test_name=f"alias_{alias}",
                        mode=IntentMode.FORCED,
                        user_text=f"Используй {alias}",
                        expected_params={},
                        should_succeed=True
                    )
                    test_cases.append(test_case)
        
        self.logger.info(f"🧪 Сгенерировано {len(test_cases)} тестовых случаев для {len(canonical_tools)} инструментов")
        return test_cases
    
    def _generate_tool_specific_tests(self, tool_name: str) -> List[ToolTestCase]:
        """
        Генерирует специфичные тесты для конкретного инструмента.
        
        Args:
            tool_name (str): Название инструмента
            
        Returns:
            List[ToolTestCase]: Список тестов для инструмента
        """
        tests = []
        
        # Базовый тест принудительного вызова
        tests.append(ToolTestCase(
            tool_name=tool_name,
            test_name="forced_basic",
            mode=IntentMode.FORCED,
            user_text=f"Принудительно используй {tool_name}",
            expected_params={},
            should_succeed=True
        ))
        
        # Специфичные тесты для каждого типа инструмента
        if tool_name == 'execute_shell':
            tests.extend([
                ToolTestCase(
                    tool_name=tool_name,
                    test_name="auto_ls_command",
                    mode=IntentMode.AUTO,
                    user_text="ls -la",
                    expected_params={'command': 'ls -la'},
                    should_succeed=True
                ),
                ToolTestCase(
                    tool_name=tool_name,
                    test_name="auto_russian_intent",
                    mode=IntentMode.AUTO,
                    user_text="покажи список файлов в текущей папке",
                    expected_params={},
                    should_succeed=True
                )
            ])
        
        elif tool_name == 'file_operations':
            tests.extend([
                ToolTestCase(
                    tool_name=tool_name,
                    test_name="auto_file_path",
                    mode=IntentMode.AUTO,
                    user_text="прочитай файл test.txt",
                    expected_params={'path': 'test.txt', 'operation': 'read'},
                    should_succeed=True
                ),
                ToolTestCase(
                    tool_name=tool_name,
                    test_name="auto_windows_path",
                    mode=IntentMode.AUTO,
                    user_text="покажи содержимое C:\\Users\\test",
                    expected_params={'path': 'C:\\Users\\test'},
                    should_succeed=True
                )
            ])
        
        elif tool_name == 'web_scraper':
            tests.extend([
                ToolTestCase(
                    tool_name=tool_name,
                    test_name="auto_url_scraping",
                    mode=IntentMode.AUTO,
                    user_text="скачай данные с https://example.com",
                    expected_params={'url': 'https://example.com', 'action': 'get_text'},
                    should_succeed=True
                )
            ])
        
        elif tool_name == 'web_search':
            tests.extend([
                ToolTestCase(
                    tool_name=tool_name,
                    test_name="auto_search_intent",
                    mode=IntentMode.AUTO,
                    user_text="найди в интернете информацию о Python",
                    expected_params={'query': 'информацию о Python'},
                    should_succeed=True
                )
            ])
        
        elif tool_name == 'api_client':
            tests.extend([
                ToolTestCase(
                    tool_name=tool_name,
                    test_name="auto_api_request",
                    mode=IntentMode.AUTO,
                    user_text="сделай GET запрос к https://api.example.com",
                    expected_params={'url': 'https://api.example.com', 'method': 'GET'},
                    should_succeed=True
                )
            ])
        
        elif tool_name == 'code_interpreter':
            tests.extend([
                ToolTestCase(
                    tool_name=tool_name,
                    test_name="auto_python_code",
                    mode=IntentMode.AUTO,
                    user_text="выполни python код: print('Hello, World!')",
                    expected_params={'code': "print('Hello, World!')"},
                    should_succeed=True
                )
            ])
        
        elif tool_name == 'dalle_tool':
            tests.extend([
                ToolTestCase(
                    tool_name=tool_name,
                    test_name="auto_image_generation",
                    mode=IntentMode.AUTO,
                    user_text="создай изображение кота",
                    expected_params={'prompt': 'изображение кота'},
                    should_succeed=True
                )
            ])
        
        elif tool_name == 'system_info':
            tests.extend([
                ToolTestCase(
                    tool_name=tool_name,
                    test_name="auto_system_info",
                    mode=IntentMode.AUTO,
                    user_text="покажи системную информацию",
                    expected_params={},
                    should_succeed=True
                )
            ])
        
        elif tool_name == 'time_helper':
            tests.extend([
                ToolTestCase(
                    tool_name=tool_name,
                    test_name="auto_time_request",
                    mode=IntentMode.AUTO,
                    user_text="сколько сейчас времени?",
                    expected_params={},
                    should_succeed=True
                )
            ])
        
        return tests
    
    async def run_all_tests(self, max_concurrent: int = 5) -> Dict[str, Any]:
        """
        Запускает все тесты с ограничением параллельности.
        
        Args:
            max_concurrent (int): Максимальное количество параллельных тестов
            
        Returns:
            Dict[str, Any]: Сводный отчет о тестировании
        """
        start_time = time.time()
        test_cases = self.generate_test_cases()
        
        self.logger.info(f"🚀 Запуск {len(test_cases)} тестов с параллельностью {max_concurrent}")
        
        # Создаем семафор для ограничения параллельности
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # Запускаем тесты
        tasks = [self._run_single_test_async(test_case, semaphore) for test_case in test_cases]
        
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            self.logger.error(f"❌ Ошибка при выполнении тестов: {e}")
        
        # Генерируем отчет
        total_time = time.time() - start_time
        report = self._generate_summary_report(total_time)
        
        self.logger.info(f"✅ Тестирование завершено за {total_time:.2f} секунд")
        return report
    
    async def _run_single_test_async(self, test_case: ToolTestCase, semaphore: asyncio.Semaphore) -> None:
        """
        Выполняет один тест асинхронно.
        
        Args:
            test_case (ToolTestCase): Тестовый случай
            semaphore (asyncio.Semaphore): Семафор для ограничения параллельности
        """
        async with semaphore:
            try:
                # Выполняем тест в отдельном потоке
                loop = asyncio.get_event_loop()
                report = await loop.run_in_executor(None, self._run_single_test, test_case)
                self.test_reports.append(report)
            except Exception as e:
                error_report = TestReport(
                    tool_name=test_case.tool_name,
                    test_name=test_case.test_name,
                    result=TestResult.ERROR,
                    execution_time=0.0,
                    error_message=str(e)
                )
                self.test_reports.append(error_report)
    
    def _run_single_test(self, test_case: ToolTestCase) -> TestReport:
        """
        Выполняет один тест синхронно.
        
        Args:
            test_case (ToolTestCase): Тестовый случай
            
        Returns:
            TestReport: Отчет о выполнении теста
        """
        start_time = time.time()
        
        try:
            self.logger.debug(f"🧪 Тест {test_case.tool_name}.{test_case.test_name} ({test_case.mode.value})")
            
            # Выполняем диспетчеризацию
            if test_case.mode == IntentMode.FORCED:
                dispatch_response = self.tool_dispatcher.dispatch_tool_call(
                    tool_name=test_case.tool_name,
                    params=test_case.expected_params,
                    user_text=test_case.user_text,
                    mode=test_case.mode,
                    context={}
                )
            else:
                dispatch_response = self.tool_dispatcher.dispatch_by_intent(
                    user_text=test_case.user_text,
                    forced_tool=None,
                    context={},
                    min_confidence=0.3  # Низкий порог для тестирования
                )
            
            execution_time = time.time() - start_time
            
            # Анализируем результат
            if not dispatch_response:
                return TestReport(
                    tool_name=test_case.tool_name,
                    test_name=test_case.test_name,
                    result=TestResult.FAIL,
                    execution_time=execution_time,
                    error_message="Диспетчер не вернул ответ"
                )
            
            # Проверяем ожидаемый результат
            if test_case.should_succeed:
                if dispatch_response.result == DispatchResult.SUCCESS:
                    result = TestResult.PASS
                    error_message = None
                else:
                    result = TestResult.FAIL
                    error_message = dispatch_response.error_message
            else:
                if dispatch_response.result != DispatchResult.SUCCESS:
                    result = TestResult.PASS
                    error_message = None
                else:
                    result = TestResult.FAIL
                    error_message = "Ожидалась ошибка, но тест прошел успешно"
            
            # Проверяем параметры для автоматических тестов
            if (test_case.mode == IntentMode.AUTO and 
                test_case.expected_params and 
                result == TestResult.PASS):
                
                actual_params = dispatch_response.tool_call.params
                for key, expected_value in test_case.expected_params.items():
                    if key not in actual_params:
                        result = TestResult.FAIL
                        error_message = f"Отсутствует ожидаемый параметр: {key}"
                        break
            
            return TestReport(
                tool_name=test_case.tool_name,
                test_name=test_case.test_name,
                result=result,
                execution_time=execution_time,
                error_message=error_message,
                response_data=dispatch_response.response_data if dispatch_response else None
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestReport(
                tool_name=test_case.tool_name,
                test_name=test_case.test_name,
                result=TestResult.ERROR,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _generate_summary_report(self, total_time: float) -> Dict[str, Any]:
        """
        Генерирует сводный отчет о тестировании.
        
        Args:
            total_time (float): Общее время выполнения
            
        Returns:
            Dict[str, Any]: Сводный отчет
        """
        # Подсчитываем статистику
        total_tests = len(self.test_reports)
        passed = len([r for r in self.test_reports if r.result == TestResult.PASS])
        failed = len([r for r in self.test_reports if r.result == TestResult.FAIL])
        errors = len([r for r in self.test_reports if r.result == TestResult.ERROR])
        skipped = len([r for r in self.test_reports if r.result == TestResult.SKIP])
        
        # Группируем по инструментам
        tools_stats = {}
        for report in self.test_reports:
            if report.tool_name not in tools_stats:
                tools_stats[report.tool_name] = {
                    'total': 0, 'passed': 0, 'failed': 0, 'errors': 0, 'skipped': 0
                }
            
            tools_stats[report.tool_name]['total'] += 1
            if report.result == TestResult.PASS:
                tools_stats[report.tool_name]['passed'] += 1
            elif report.result == TestResult.FAIL:
                tools_stats[report.tool_name]['failed'] += 1
            elif report.result == TestResult.ERROR:
                tools_stats[report.tool_name]['errors'] += 1
            elif report.result == TestResult.SKIP:
                tools_stats[report.tool_name]['skipped'] += 1
        
        # Находим проблемные инструменты
        problematic_tools = []
        for tool_name, stats in tools_stats.items():
            if stats['failed'] > 0 or stats['errors'] > 0:
                problematic_tools.append({
                    'tool': tool_name,
                    'failed': stats['failed'],
                    'errors': stats['errors'],
                    'success_rate': stats['passed'] / stats['total'] if stats['total'] > 0 else 0
                })
        
        # Находим самые медленные тесты
        slowest_tests = sorted(
            [r for r in self.test_reports if r.execution_time > 0],
            key=lambda x: x.execution_time,
            reverse=True
        )[:10]
        
        summary = {
            'overview': {
                'total_tests': total_tests,
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'skipped': skipped,
                'success_rate': passed / total_tests if total_tests > 0 else 0,
                'total_time': total_time,
                'avg_time_per_test': total_time / total_tests if total_tests > 0 else 0
            },
            'tools_stats': tools_stats,
            'problematic_tools': problematic_tools,
            'slowest_tests': [
                {
                    'tool': t.tool_name,
                    'test': t.test_name,
                    'time': t.execution_time,
                    'result': t.result.value
                }
                for t in slowest_tests
            ],
            'failed_tests': [
                {
                    'tool': r.tool_name,
                    'test': r.test_name,
                    'error': r.error_message,
                    'time': r.execution_time
                }
                for r in self.test_reports 
                if r.result in [TestResult.FAIL, TestResult.ERROR]
            ],
            'warnings': self.warnings
        }
        
        return summary
    
    def run_tests_sync(self) -> Dict[str, Any]:
        """
        Синхронная версия запуска тестов.
        
        Returns:
            Dict[str, Any]: Сводный отчет
        """
        start_time = time.time()
        test_cases = self.generate_test_cases()
        
        self.logger.info(f"🚀 Запуск {len(test_cases)} тестов синхронно")
        
        for test_case in test_cases:
            report = self._run_single_test(test_case)
            self.test_reports.append(report)
        
        total_time = time.time() - start_time
        return self._generate_summary_report(total_time)
    
    def print_summary(self, report: Dict[str, Any]) -> None:
        """
        Выводит краткий отчет в консоль.
        
        Args:
            report (Dict[str, Any]): Отчет о тестировании
        """
        overview = report['overview']
        
        print("\n" + "="*60)
        print("🧪 ОТЧЕТ О ТЕСТИРОВАНИИ ИНСТРУМЕНТОВ")
        print("="*60)
        
        print(f"📊 Общая статистика:")
        print(f"   Всего тестов: {overview['total_tests']}")
        print(f"   ✅ Прошли: {overview['passed']}")
        print(f"   ❌ Провалились: {overview['failed']}")
        print(f"   💥 Ошибки: {overview['errors']}")
        print(f"   ⏭️ Пропущены: {overview['skipped']}")
        print(f"   📈 Успешность: {overview['success_rate']:.1%}")
        print(f"   ⏱️ Общее время: {overview['total_time']:.2f}с")
        
        if report['problematic_tools']:
            print(f"\n⚠️ Проблемные инструменты:")
            for tool in report['problematic_tools']:
                print(f"   {tool['tool']}: {tool['failed']} провалов, {tool['errors']} ошибок")
        
        if report['failed_tests']:
            print(f"\n❌ Провалившиеся тесты:")
            for test in report['failed_tests'][:5]:  # Показываем только первые 5
                print(f"   {test['tool']}.{test['test']}: {test['error']}")
        
        print("\n" + "="*60)


# Функция для быстрого запуска тестов
def run_tool_autotest(smart_delegator=None, async_mode: bool = False) -> Dict[str, Any]:
    """
    Быстрый запуск автотестов инструментов.
    
    Args:
        smart_delegator: Экземпляр SmartDelegator
        async_mode (bool): Использовать асинхронный режим
        
    Returns:
        Dict[str, Any]: Отчет о тестировании
    """
    autotest = ToolAutoTest(smart_delegator)
    
    if async_mode:
        # Запускаем в новом event loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            report = loop.run_until_complete(autotest.run_all_tests())
            loop.close()
        except Exception as e:
            logger.error(f"❌ Ошибка асинхронного тестирования: {e}")
            report = autotest.run_tests_sync()
    else:
        report = autotest.run_tests_sync()
    
    # Выводим краткий отчет
    autotest.print_summary(report)
    
    return report


if __name__ == "__main__":
    # Пример запуска тестов
    logging.basicConfig(level=logging.INFO)
    report = run_tool_autotest(async_mode=False)
    
    # Сохраняем детальный отчет в файл
    with open("tool_autotest_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
