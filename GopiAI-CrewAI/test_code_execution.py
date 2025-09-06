#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы code_execution с Gemini API
Следует официальной документации: https://ai.google.dev/gemini-api/docs/code-execution
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ .env файл загружен из: {env_path}")
else:
    print(f"❌ .env файл не найден: {env_path}")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_gemini_sdk():
    """Тестируем прямое использование Google Gemini SDK с code_execution"""
    try:
        from google import genai
        from google.genai import types
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY не найден")
            return False
            
        print(f"🔑 API ключ найден: {api_key[:10]}...")
        
        # Создаем клиент
        client = genai.Client(api_key=api_key)
        print("✅ Gemini клиент создан")
        
        # Тестовый запрос с code_execution
        test_prompt = (
            "Вычисли сумму первых 10 простых чисел. "
            "Сгенерируй и выполни код для этого вычисления."
        )
        
        print(f"📝 Отправляем запрос: {test_prompt}")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=test_prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(code_execution=types.ToolCodeExecution())]
            ),
        )
        
        print("✅ Ответ получен от Gemini!")
        
        # Выводим все части ответа
        for i, part in enumerate(response.candidates[0].content.parts):
            print(f"\n--- Часть {i+1} ---")
            
            if part.text is not None:
                print("📝 Текст:")
                print(part.text)
            
            if part.executable_code is not None:
                print("🐍 Исполняемый код:")
                print(part.executable_code.code)
            
            if part.code_execution_result is not None:
                print("📊 Результат выполнения:")
                print(part.code_execution_result.output)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Gemini SDK: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crewai_gemini():
    """Тестируем наш CrewAI Gemini провайдер"""
    try:
        from gopiai.llm.crewai_gemini import create_crewai_gemini_llm
        
        print("🚀 Создаем CrewAI Gemini LLM...")
        
        llm = create_crewai_gemini_llm(
            model="gemini-2.5-flash",
            enable_code_execution=True,
            temperature=0.7
        )
        
        print("✅ CrewAI Gemini LLM создан")
        
        # Тестовый запрос
        from langchain_core.messages import HumanMessage
        
        test_message = HumanMessage(
            content="Вычисли площадь круга с радиусом 5. Сгенерируй и выполни код."
        )
        
        print("📝 Отправляем тестовое сообщение...")
        
        result = llm._generate([test_message])
        
        print("✅ Ответ получен!")
        print("📋 Результат:")
        print(result.generations[0].message.content)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования CrewAI Gemini: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_math():
    """Простой тест математических вычислений"""
    try:
        from gopiai.llm.gemini_provider import create_gemini_provider
        
        print("🧮 Тестируем простые математические вычисления...")
        
        provider = create_gemini_provider(
            model="gemini-2.5-flash",
            enable_code_execution=True
        )
        
        result = provider.generate_content(
            "Посчитай 123 * 456 и выведи результат в формате: '123 * 456 = X'"
        )
        
        print("✅ Результат:")
        print(result)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка простого теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Запуск тестов code_execution для Gemini API")
    print("=" * 60)
    
    tests = [
        ("Прямой Gemini SDK", test_direct_gemini_sdk),
        ("CrewAI Gemini LLM", test_crewai_gemini),
        ("Простая математика", test_simple_math),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Тест: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                print(f"✅ {test_name}: ПРОШЕЛ")
                passed += 1
            else:
                print(f"❌ {test_name}: ПРОВАЛЕН")
        except Exception as e:
            print(f"💥 {test_name}: ОШИБКА - {e}")
    
    print(f"\n📊 Результат: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("🎉 Все тесты прошли! code_execution работает корректно!")
    else:
        print("⚠️ Некоторые тесты провалены. Проверьте настройки.")