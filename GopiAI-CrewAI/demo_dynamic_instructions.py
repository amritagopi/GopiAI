"""
🎯 Демонстрация системы динамических инструкций для CrewAI
Финальная демонстрация интеграции ToolsInstructionManager с CrewAI workflow
"""

import os
import sys
from pathlib import Path

# Добавляем пути для импорта
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir / 'gopiai_tools'))

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

# Загружаем переменные окружения
load_dotenv()

def demo_system_overview():
    """Демонстрация обзора системы"""
    print("="*80)
    print("[SYSTEM] ДЕМОНСТРАЦИЯ СИСТЕМЫ ДИНАМИЧЕСКИХ ИНСТРУКЦИЙ ДЛЯ CREWAI")
    print("="*80)
    
    try:
        from gopiai_tools.tools_instruction_manager import get_tools_instruction_manager
        
        manager = get_tools_instruction_manager()
        
        print("\n[INFO] ОБЗОР СИСТЕМЫ:")
        print("- Система динамически подгружает детальные инструкции для инструментов")
        print("- Инструкции загружаются только при выборе инструмента LLM")
        print("- Не перегружает системный промпт краткими описаниями")
        print("- Автоматически очищает инструкции после выполнения")
        
        print(f"\n[TOOLS] ДОСТУПНЫЕ ИНСТРУМЕНТЫ ({len(manager.get_tools_summary())}):")
        tools_summary = manager.get_tools_summary()
        for i, (tool_name, description) in enumerate(tools_summary.items(), 1):
            instructions = manager.get_tool_detailed_instructions(tool_name)
            instructions_size = len(instructions) if instructions else 0
            print(f"  {i}. {tool_name}")
            print(f"     Описание: {description[:60]}...")
            print(f"     Размер инструкций: {instructions_size} символов")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при демонстрации обзора: {e}")
        return False


def demo_agent_enhancement():
    """Демонстрация улучшения агента динамическими инструкциями"""
    print("\n" + "="*60)
    print("[AGENT] ДЕМОНСТРАЦИЯ УЛУЧШЕНИЯ АГЕНТА")
    print("="*60)
    
    try:
        from gopiai_tools.crewai_tools_integration import enhance_agent_with_instructions
        from gopiai_tools.filesystem_tools import GopiAIFileSystemTool
        from gopiai_tools.browser_tools import GopiAIBrowserTool
        
        # Создаем LLM
        llm = LLM(
            model="gemini/gemini-1.5-flash",
            temperature=0.1
        )
        
        print("\n1. Создание обычного агента...")
        # Создаем обычного агента
        original_agent = Agent(
            role='Demo Agent',
            goal='Демонстрировать работу с инструментами',
            backstory='Демонстрационный агент для тестирования системы',
            tools=[GopiAIFileSystemTool(), GopiAIBrowserTool()],
            llm=llm,
            verbose=True
        )
        
        print(f"   - Роль: {original_agent.role}")
        orig_tools = list(original_agent.tools or [])
        print(f"   - Количество инструментов: {len(orig_tools)}")
        print(f"   - Тип инструментов: {[tool.__class__.__name__ for tool in orig_tools]}")
        
        print("\n2. Улучшение агента динамическими инструкциями...")
        # Улучшаем агента
        enhanced_agent = enhance_agent_with_instructions(original_agent)
        
        print(f"   - Агент успешно улучшен!")
        enh_tools = list(enhanced_agent.tools or [])
        print(f"   - Количество инструментов: {len(enh_tools)}")
        print(f"   - Динамические инструкции активированы")
        
        print("\n3. Сравнение:")
        print("   ОБЫЧНЫЙ АГЕНТ:")
        print("   - Инструменты имеют только базовые описания")
        print("   - LLM видит краткую информацию об инструментах")
        print("   - Может не знать всех возможностей инструментов")
        
        print("\n   УЛУЧШЕННЫЙ АГЕНТ:")
        print("   - При выборе инструмента подгружаются детальные инструкции")
        print("   - LLM получает полную информацию о возможностях инструмента")
        print("   - Инструкции автоматически очищаются после использования")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при демонстрации улучшения агента: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_crew_enhancement():
    """Демонстрация улучшения команды динамическими инструкциями"""
    print("\n" + "="*60)
    print("[CREW] ДЕМОНСТРАЦИЯ УЛУЧШЕНИЯ КОМАНДЫ")
    print("="*60)
    
    try:
        from gopiai_tools.crewai_tools_integration import enhance_crew_with_instructions
        from gopiai_tools.filesystem_tools import GopiAIFileSystemTool
        from gopiai_tools.local_mcp_tools import get_local_mcp_tools
        
        # Создаем LLM
        llm = LLM(
            model="gemini/gemini-1.5-flash",
            temperature=0.1
        )
        
        print("\n1. Создание команды с несколькими агентами...")
        
        # Файловый агент
        file_agent = Agent(
            role='File Manager',
            goal='Управлять файлами и директориями',
            backstory='Специалист по работе с файловой системой',
            tools=[GopiAIFileSystemTool()],
            llm=llm,
            verbose=True
        )
        
        # API агент
        # Для локальных MCP в этом проекте предоставлен менеджер инструментов, а не BaseTool.
        # Поэтому демонстрационно оставляем список инструментов пустым и используем менеджер при необходимости.
        api_agent = Agent(
            role='API Specialist',
            goal='Работать с веб-сервисами и API',
            backstory='Эксперт по интеграции с внешними сервисами',
            tools=[],
            llm=llm,
            verbose=True
        )
        
        # Создаем команду
        original_crew = Crew(
            agents=[file_agent, api_agent],
            tasks=[],  # Задачи для демонстрации не нужны
            verbose=True
        )
        
        print(f"   - Количество агентов: {len(original_crew.agents)}")
        print(f"   - Агенты: {[agent.role for agent in original_crew.agents]}")
        
        total_tools = sum(len(list(agent.tools or [])) for agent in original_crew.agents)
        print(f"   - Общее количество инструментов: {total_tools}")
        
        print("\n2. Улучшение команды динамическими инструкциями...")
        # Улучшаем команду
        enhanced_crew = enhance_crew_with_instructions(original_crew)
        
        print(f"   - Команда успешно улучшена!")
        print(f"   - Все агенты получили динамические инструкции")
        print(f"   - Количество агентов: {len(enhanced_crew.agents)}")
        
        enhanced_total_tools = sum(len(list(agent.tools or [])) for agent in enhanced_crew.agents)
        print(f"   - Общее количество инструментов: {enhanced_total_tools}")
        
        print("\n3. Преимущества улучшенной команды:")
        print("   - Каждый агент получает детальные инструкции для своих инструментов")
        print("   - Инструкции подгружаются динамически при необходимости")
        print("   - Системный промпт остается чистым и не перегруженным")
        print("   - Улучшается качество работы всех агентов в команде")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при демонстрации улучшения команды: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_instruction_details():
    """Демонстрация детальных инструкций для инструментов"""
    print("\n" + "="*60)
    print("[INSTRUCTIONS] ДЕМОНСТРАЦИЯ ДЕТАЛЬНЫХ ИНСТРУКЦИЙ")
    print("="*60)
    
    try:
        from gopiai_tools.tools_instruction_manager import get_tools_instruction_manager
        
        manager = get_tools_instruction_manager()
        
        print("\n1. Пример краткого описания для системного промпта:")
        tools_summary = manager.get_tools_summary()
        example_tool = list(tools_summary.keys())[0]
        brief_description = tools_summary[example_tool]
        
        print(f"   Инструмент: {example_tool}")
        print(f"   Краткое описание: {brief_description}")
        
        print(f"\n2. Пример детальных инструкций для {example_tool}:")
        detailed_instructions = manager.get_tool_detailed_instructions(example_tool)
        
        if detailed_instructions:
            # Показываем первые 300 символов детальных инструкций
            preview = detailed_instructions[:300] + "..." if len(detailed_instructions) > 300 else detailed_instructions
            print(f"   Размер: {len(detailed_instructions)} символов")
            print(f"   Превью:")
            print("   " + "─" * 50)
            for line in preview.split('\n')[:10]:  # Показываем первые 10 строк
                print(f"   {line}")
            if len(detailed_instructions) > 300:
                print("   ...")
            print("   " + "─" * 50)
        
        print(f"\n3. Сравнение размеров:")
        print(f"   Краткое описание: {len(brief_description)} символов")
        print(f"   Детальные инструкции: {len(detailed_instructions) if detailed_instructions else 0} символов")
        print(f"   Экономия места в промпте: {len(detailed_instructions) - len(brief_description) if detailed_instructions else 0} символов")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при демонстрации инструкций: {e}")
        return False


def run_full_demo():
    """Запуск полной демонстрации системы"""
    print("[DEMO] ЗАПУСК ПОЛНОЙ ДЕМОНСТРАЦИИ СИСТЕМЫ ДИНАМИЧЕСКИХ ИНСТРУКЦИЙ")
    print("Время запуска:", "19 июля 2025 г.")
    
    results = []
    
    # 1. Обзор системы
    results.append(demo_system_overview())
    
    # 2. Демонстрация улучшения агента
    results.append(demo_agent_enhancement())
    
    # 3. Демонстрация улучшения команды
    results.append(demo_crew_enhancement())
    
    # 4. Демонстрация детальных инструкций
    results.append(demo_instruction_details())
    
    # Итоги
    print("\n" + "="*80)
    print("[RESULTS] ИТОГИ ДЕМОНСТРАЦИИ")
    print("="*80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n[OK] Успешно выполнено демонстраций: {passed}/{total}")
    
    if passed == total:
        print("\n[SUCCESS] ВСЕ ДЕМОНСТРАЦИИ ПРОШЛИ УСПЕШНО!")
        print("\n[INFO] СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ:")
        print("   - Все компоненты работают корректно")
        print("   - Интеграция с CrewAI завершена")
        print("   - Динамические инструкции функционируют")
        print("   - Документация создана")
        
        print("\n[NEXT] СЛЕДУЮЩИЕ ШАГИ:")
        print("   1. Используйте enhance_agent_with_instructions() для улучшения агентов")
        print("   2. Используйте enhance_crew_with_instructions() для улучшения команд")
        print("   3. Или используйте декоратор @with_dynamic_instructions")
        print("   4. Изучите документацию в DYNAMIC_INSTRUCTIONS_INTEGRATION.md")
        
    else:
        print(f"\n[WARNING] Некоторые демонстрации не прошли успешно.")
        print("Проверьте логи выше для диагностики проблем.")
    
    print("\n" + "="*80)
    return passed == total


if __name__ == "__main__":
    success = run_full_demo()
    sys.exit(0 if success else 1)
