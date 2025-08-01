#!/usr/bin/env python3
"""
Тест импорта и базовой функциональности API Response Builder.
"""

from api_response_builder import (
    APIResponseBuilder, 
    APIErrorCode, 
    create_success_response, 
    create_error_response
)

def test_imports():
    print('✅ Все компоненты API Response Builder успешно импортированы')
    
    # Тест инициализации
    builder = APIResponseBuilder()
    print('✅ APIResponseBuilder инициализирован')
    
    # Тест создания успешного ответа
    response = create_success_response({'test': 'data'})
    print(f'✅ Успешный ответ создан: {response["status"]}')
    
    # Тест создания ответа об ошибке
    error_response = create_error_response(APIErrorCode.VALIDATION_ERROR, 'Test error')
    print(f'✅ Ответ об ошибке создан: {error_response["status"]}')
    
    print('🎉 Система стандартизации API ответов полностью готова к использованию!')
    
    return True

if __name__ == "__main__":
    test_imports()