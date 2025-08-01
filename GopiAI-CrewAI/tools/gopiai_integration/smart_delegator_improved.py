    def _call_llm_with_tools(self, messages: List[Dict], tools: List[Dict], max_iterations: int = 5) -> str:
        """
        Улучшенная реализация вызова LLM с нативной поддержкой OpenAI Tool Calling.
        Реализует двухфазную обработку: tool execution → final response generation.
        Включает ограничения итераций для предотвращения бесконечных циклов.

        Args:
            messages: Список сообщений для LLM
            tools: Схемы доступных инструментов в формате OpenAI
            max_iterations: Максимальное количество итераций tool calling (по умолчанию 5)

        Returns:
            str: Финальный ответ от LLM
        """
        logger.info(f"[TOOL-CALLING] Начало _call_llm_with_tools, max_iterations={max_iterations}")
        current_messages = messages.copy()
        iteration = 0
        total_tool_calls = 0  # Счётчик общего количества вызовов инструментов

        try:
            # Определяем модель для использования
            model_id = self._get_model_for_request(current_messages)
            logger.info(f"[TOOL-CALLING] Используем модель: {model_id}")

            while iteration < max_iterations:
                iteration += 1
                logger.info(f"[TOOL-CALLING] Итерация {iteration}/{max_iterations}")

                # Фаза 1: Вызов LLM с инструментами (с retry логикой)
                try:
                    response = self._retry_with_backoff(
                        lambda: self._make_llm_request(model_id, current_messages, tools),
                        max_retries=3,
                        base_delay=1.0
                    )
                except Exception as e:
                    logger.error(f"[TOOL-CALLING] Ошибка при вызове LLM на итерации {iteration}: {e}")
                    return f"Ошибка при вызове языковой модели: {str(e)}"

                if not response or not response.choices:
                    logger.error("[TOOL-CALLING] Пустой ответ от LLM")
                    return "Ошибка: пустой ответ от языковой модели"

                message = response.choices[0].message
                response_text = message.content or ""
                tool_calls = getattr(message, 'tool_calls', None)

                logger.info(f"[TOOL-CALLING] Получен ответ: text_length={len(response_text)}, tool_calls={len(tool_calls) if tool_calls else 0}")

                # Если нет вызовов инструментов, возвращаем финальный ответ
                if not tool_calls:
                    logger.info("[TOOL-CALLING] Нет вызовов инструментов, возвращаем финальный ответ")
                    return response_text or "Пустой ответ от модели"

                # Фаза 2: Выполнение инструментов
                logger.info(f"[TOOL-CALLING] Выполняем {len(tool_calls)} вызовов инструментов")
                total_tool_calls += len(tool_calls)

                # Проверяем общий лимит вызовов инструментов
                if total_tool_calls > 20:  # Защита от слишком большого количества вызовов
                    logger.warning(f"[TOOL-CALLING] Превышен лимит общих вызовов инструментов: {total_tool_calls}")
                    return f"Превышен лимит вызовов инструментов ({total_tool_calls}). Обработка остановлена."

                # Добавляем сообщение ассистента с tool_calls
                assistant_message = {
                    "role": "assistant",
                    "content": response_text,
                    "tool_calls": []
                }

                # Обрабатываем каждый tool_call с улучшенной обработкой ошибок
                for tc in tool_calls:
                    try:
                        assistant_message["tool_calls"].append({
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        })
                    except AttributeError as e:
                        logger.error(f"[TOOL-CALLING] Ошибка структуры tool_call: {e}")
                        # Пропускаем некорректные tool_calls
                        continue

                current_messages.append(assistant_message)

                # Выполняем каждый вызов инструмента с улучшенной обработкой ошибок
                tool_results = []
                for tool_call in tool_calls:
                    try:
                        # Добавляем валидацию структуры tool_call
                        if not hasattr(tool_call, 'function') or not hasattr(tool_call.function, 'name'):
                            logger.error("[TOOL-CALLING] Некорректная структура tool_call")
                            tool_results.append({
                                "tool_call_id": getattr(tool_call, 'id', 'unknown'),
                                "role": "tool",
                                "name": "unknown",
                                "content": "Ошибка: некорректная структура вызова инструмента"
                            })
                            continue

                        result = self._execute_tool_call(tool_call)
                        
                        # Ограничиваем размер результата для предотвращения переполнения контекста
                        result_str = str(result)
                        if len(result_str) > 4000:  # Лимит на размер результата
                            result_str = result_str[:4000] + "\n... (результат обрезан из-за большого размера)"
                            logger.info(f"[TOOL-CALLING] Результат инструмента {tool_call.function.name} обрезан до 4000 символов")

                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_call.function.name,
                            "content": result_str
                        })
                        logger.info(f"[TOOL-CALLING] Инструмент {tool_call.function.name} выполнен успешно")
                        
                    except Exception as e:
                        logger.error(f"[TOOL-CALLING] Ошибка выполнения инструмента {getattr(tool_call.function, 'name', 'unknown')}: {e}")
                        tool_results.append({
                            "tool_call_id": getattr(tool_call, 'id', 'unknown'),
                            "role": "tool",
                            "name": getattr(tool_call.function, 'name', 'unknown'),
                            "content": f"Ошибка выполнения: {str(e)}"
                        })

                # Добавляем результаты инструментов к сообщениям
                current_messages.extend(tool_results)

                # Проверяем размер контекста для предотвращения переполнения
                total_context_size = sum(len(str(msg.get('content', ''))) for msg in current_messages)
                if total_context_size > 50000:  # Лимит на общий размер контекста
                    logger.warning(f"[TOOL-CALLING] Размер контекста превышает лимит: {total_context_size}")
                    # Обрезаем старые сообщения, оставляя системный промпт и последние сообщения
                    system_msg = current_messages[0] if current_messages and current_messages[0].get('role') == 'system' else None
                    recent_messages = current_messages[-10:]  # Последние 10 сообщений
                    current_messages = ([system_msg] if system_msg else []) + recent_messages
                    logger.info("[TOOL-CALLING] Контекст обрезан для предотвращения переполнения")

                # Продолжаем цикл для следующей итерации
                logger.info(f"[TOOL-CALLING] Итерация {iteration} завершена, продолжаем...")

            # Если достигли максимального количества итераций
            logger.warning(f"[TOOL-CALLING] Достигнуто максимальное количество итераций ({max_iterations})")
            
            # Фаза 3: Финальная генерация ответа без инструментов
            logger.info("[TOOL-CALLING] Генерируем финальный ответ без инструментов")
            try:
                final_response = self._retry_with_backoff(
                    lambda: self._make_llm_request(model_id, current_messages, tools=None),
                    max_retries=3,
                    base_delay=1.0
                )
                
                if final_response and final_response.choices:
                    final_text = final_response.choices[0].message.content
                    if final_text:
                        logger.info("[TOOL-CALLING] Финальный ответ успешно сгенерирован")
                        return final_text
                    else:
                        logger.warning("[TOOL-CALLING] Финальный ответ пуст")
                        return "Достигнуто максимальное количество итераций инструментов. Обработка завершена."
                else:
                    logger.error("[TOOL-CALLING] Не удалось получить финальный ответ")
                    return "Не удалось сгенерировать финальный ответ после выполнения инструментов."
                    
            except Exception as e:
                logger.error(f"[TOOL-CALLING] Ошибка при генерации финального ответа: {e}")
                return f"Ошибка при генерации финального ответа: {str(e)}"

        except Exception as e:
            logger.error(f"[TOOL-CALLING] Критическая ошибка в _call_llm_with_tools: {e}")
            logger.error(f"[TOOL-CALLING] Traceback: {traceback.format_exc()}")
            return f"Ошибка при обработке запроса с инструментами: {str(e)}"

    def _execute_tool_call(self, tool_call):
        """
        Выполняет вызов инструмента с улучшенным парсингом JSON аргументов и обработкой ошибок

        Args:
            tool_call: Объект вызова инструмента от LLM

        Returns:
            Результат выполнения инструмента
        """
        function_name = "unknown"
        try:
            # Проверяем структуру tool_call
            if not hasattr(tool_call, 'function'):
                logger.error("[TOOL-EXEC] tool_call не содержит атрибут 'function'")
                return "Ошибка: некорректная структура вызова инструмента"

            function_name = tool_call.function.name
            arguments_str = tool_call.function.arguments

            logger.info(f"[TOOL-EXEC] Выполняем инструмент: {function_name}")
            logger.debug(f"[TOOL-EXEC] Аргументы (raw): {arguments_str}")

            # Улучшенный парсинг JSON аргументов с обработкой различных форматов
            arguments = {}
            try:
                if isinstance(arguments_str, str):
                    # Очищаем строку от возможных проблемных символов
                    cleaned_args = arguments_str.strip()
                    if not cleaned_args:
                        arguments = {}
                    elif cleaned_args.startswith('{') and cleaned_args.endswith('}'):
                        arguments = json.loads(cleaned_args)
                    else:
                        # Пытаемся обернуть в JSON если это не объект
                        try:
                            arguments = json.loads(f'{{{cleaned_args}}}')
                        except:
                            # Если всё ещё не получается, пробуем как есть
                            arguments = json.loads(cleaned_args)
                elif isinstance(arguments_str, dict):
                    arguments = arguments_str
                elif arguments_str is None:
                    arguments = {}
                else:
                    # Пытаемся преобразовать в строку и затем в JSON
                    arguments = json.loads(str(arguments_str))
                    
            except json.JSONDecodeError as e:
                logger.error(f"[TOOL-EXEC] Ошибка парсинга JSON аргументов: {e}")
                logger.error(f"[TOOL-EXEC] Проблемная строка: {repr(arguments_str)}")
                
                # Пытаемся восстановить аргументы из строки
                try:
                    # Простой парсинг для базовых случаев
                    if isinstance(arguments_str, str) and '=' in arguments_str:
                        # Формат: key=value, key2=value2
                        arguments = {}
                        for pair in arguments_str.split(','):
                            if '=' in pair:
                                key, value = pair.split('=', 1)
                                arguments[key.strip()] = value.strip().strip('"\'')
                    else:
                        return f"Ошибка парсинга аргументов инструмента: {str(e)}"
                except Exception as recovery_error:
                    logger.error(f"[TOOL-EXEC] Не удалось восстановить аргументы: {recovery_error}")
                    return f"Критическая ошибка парсинга аргументов: {str(e)}"

            logger.debug(f"[TOOL-EXEC] Аргументы (parsed): {arguments}")

            # Валидируем аргументы против схемы
            try:
                from .tool_definitions import validate_tool_call
                validation = validate_tool_call(function_name, arguments)

                if not validation['valid']:
                    logger.error(f"[TOOL-EXEC] Валидация не прошла: {validation['errors']}")
                    return f"Ошибка валидации аргументов: {'; '.join(validation['errors'])}"

                # Используем нормализованные аргументы
                normalized_args = validation['normalized_args']
                logger.debug(f"[TOOL-EXEC] Нормализованные аргументы: {normalized_args}")
                
            except Exception as validation_error:
                logger.error(f"[TOOL-EXEC] Ошибка валидации: {validation_error}")
                # Продолжаем с исходными аргументами если валидация не работает
                normalized_args = arguments

            # Инициализируем CommandExecutor если нужно
            if not hasattr(self, 'command_executor'):
                try:
                    from .command_executor import CommandExecutor
                    self.command_executor = CommandExecutor()
                    logger.debug("[TOOL-EXEC] CommandExecutor инициализирован")
                except Exception as init_error:
                    logger.error(f"[TOOL-EXEC] Ошибка инициализации CommandExecutor: {init_error}")
                    return f"Ошибка инициализации исполнителя команд: {str(init_error)}"

            # Маппинг имен инструментов на методы CommandExecutor
            tool_method_map = {
                'execute_terminal_command': 'execute_terminal_command',
                'browse_website': 'browse_website',
                'web_search': 'web_search',
                'file_operations': 'file_operations'
            }

            if function_name not in tool_method_map:
                logger.error(f"[TOOL-EXEC] Неизвестный инструмент: {function_name}")
                available_tools = list(tool_method_map.keys())
                return f"Неизвестный инструмент: {function_name}. Доступные инструменты: {', '.join(available_tools)}"

            method_name = tool_method_map[function_name]
            
            # Проверяем наличие метода
            if not hasattr(self.command_executor, method_name):
                logger.error(f"[TOOL-EXEC] Метод {method_name} не найден в CommandExecutor")
                return f"Метод {method_name} не реализован в исполнителе команд"

            method = getattr(self.command_executor, method_name)

            # Вызываем метод с нормализованными аргументами и таймаутом
            try:
                logger.info(f"[TOOL-EXEC] Вызываем {method_name} с аргументами: {normalized_args}")
                result = method(**normalized_args)
                
                # Проверяем результат
                if result is None:
                    logger.warning(f"[TOOL-EXEC] Инструмент {function_name} вернул None")
                    result = f"Инструмент {function_name} выполнен, но не вернул результат"
                
                logger.info(f"[TOOL-EXEC] Инструмент {function_name} выполнен успешно")
                logger.debug(f"[TOOL-EXEC] Результат: {str(result)[:200]}...")
                
                return result
                
            except TypeError as type_error:
                logger.error(f"[TOOL-EXEC] Ошибка типов аргументов для {function_name}: {type_error}")
                return f"Ошибка аргументов инструмента {function_name}: {str(type_error)}"
            except Exception as exec_error:
                logger.error(f"[TOOL-EXEC] Ошибка выполнения метода {method_name}: {exec_error}")
                return f"Ошибка выполнения инструмента {function_name}: {str(exec_error)}"

        except AttributeError as attr_error:
            logger.error(f"[TOOL-EXEC] Ошибка атрибутов tool_call: {attr_error}")
            return f"Ошибка структуры вызова инструмента: {str(attr_error)}"
        except Exception as e:
            logger.error(f"[TOOL-EXEC] Критическая ошибка выполнения инструмента {function_name}: {e}")
            logger.error(f"[TOOL-EXEC] Traceback: {traceback.format_exc()}")
            return f"Критическая ошибка выполнения инструмента {function_name}: {str(e)}"