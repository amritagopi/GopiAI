# Отчет о найденных методах-заглушках

Всего найдено **322** заглушек в **64** файлах.

## Список файлов с заглушками

### interfaces.py (32 заглушек)

- `to_dict` (строка 29)
- `from_dict` (строка 39)
- `system_message` (строка 52)
- `user_message` (строка 65)
- `assistant_message` (строка 78)
- `count_tokens` (строка 153)
- `count_message_tokens` (строка 165)
- `get_system_prompt` (строка 181)
- `get_user_prompt` (строка 193)
- `format_prompt` (строка 205)
- `name` (строка 234)
- `description` (строка 244)
- `parameters` (строка 254)
- `to_dict` (строка 275)
- `get_tools` (строка 288)
- `get_tool` (строка 297)
- `name` (строка 338)
- `state` (строка 348)
- `set_llm` (строка 388)
- `set_tool_provider` (строка 397)
- `set_prompt_provider` (строка 406)
- `name` (строка 432)
- `add_agent` (строка 454)
- `get_agent` (строка 464)
- `primary_agent` (строка 477)
- `create_flow` (строка 490)
- `register_agent_factory` (строка 502)
- `update` (строка 520)
- `show` (строка 525)
- `hide` (строка 530)
- `set_enabled` (строка 535)
- `on_event` (строка 548)

### utils\file_operations.py (28 заглушек)

- `get_absolute_path` (строка 28)
- `normalize_path` (строка 42)
- `get_directory_name` (строка 53)
- `get_filename` (строка 64)
- `read_text_file` (строка 82)
- `write_text_file` (строка 106)
- `append_to_file` (строка 128)
- `read_binary_file` (строка 150)
- `write_binary_file` (строка 173)
- `read_json_file` (строка 198)
- `write_json_file` (строка 222)
- `read_csv_file` (строка 246)
- `write_csv_file` (строка 278)
- `read_pickle_file` (строка 312)
- `write_pickle_file` (строка 335)
- `list_files` (строка 360)
- `safe_remove_file` (строка 391)
- `safe_make_dirs` (строка 415)
- `safe_copy_file` (строка 436)
- `safe_move_file` (строка 467)
- `create_temp_file` (строка 502)
- `create_temp_dir` (строка 526)
- `file_exists` (строка 546)
- `dir_exists` (строка 557)
- `is_empty_dir` (строка 568)
- `get_file_size` (строка 581)
- `get_file_modification_time` (строка 597)
- `is_file_newer_than` (строка 613)

### utils\common.py (18 заглушек)

- `truncate_string` (строка 29)
- `slugify` (строка 44)
- `normalize_text` (строка 59)
- `generate_hash` (строка 76)
- `chunks` (строка 99)
- `find_duplicates` (строка 111)
- `flatten` (строка 131)
- `group_by` (строка 150)
- `get_timestamp` (строка 174)
- `format_duration` (строка 185)
- `ensure_dir` (строка 210)
- `get_file_extension` (строка 219)
- `is_text_file` (строка 230)
- `is_valid_email` (строка 252)
- `is_valid_url` (строка 264)
- `safe_cast` (строка 276)
- `timed` (строка 296)
- `retry` (строка 313)

### marketing\fixed_nodes.py (17 заглушек)

- `add_successor` (строка 20)
- `_run` (строка 25)
- `prep` (строка 43)
- `exec` (строка 54)
- `post` (строка 60)
- `prep` (строка 81)
- `exec` (строка 98)
- `post` (строка 104)
- `prep` (строка 124)
- `exec` (строка 141)
- `post` (строка 147)
- `prep` (строка 165)
- `exec` (строка 179)
- `post` (строка 200)
- `prep` (строка 222)
- `exec` (строка 237)
- `post` (строка 243)

### marketing\demo.py (13 заглушек)

- `run_content_creation` (строка 19)
- `run_content_distribution` (строка 49)
- `run_content_analytics` (строка 63)
- `run_end_to_end_workflow` (строка 93)
- `_simulate_research` (строка 121)
- `_simulate_content_generation` (строка 143)
- `_simulate_optimization` (строка 182)
- `_adapt_for_channel` (строка 197)
- `_simulate_distribution` (строка 211)
- `_simulate_analytics_collection` (строка 221)
- `_simulate_analytics_insights` (строка 241)
- `_simulate_recommendations` (строка 251)
- `main` (строка 261)

### agent\personalization_manager.py (11 заглушек)

- `add_interaction` (строка 133)
- `update_content_domain` (строка 147)
- `update_frequent_task` (строка 158)
- `update_common_file` (строка 167)
- `get_preference` (строка 176)
- `set_preference` (строка 191)
- `get_top_domains` (строка 212)
- `get_top_tasks` (строка 229)
- `get_top_files` (строка 241)
- `to_dict` (строка 253)
- `from_dict` (строка 294)

### ui\chat_widget.py (11 заглушек)

- `_setup_ui` (строка 35)
- `_connect_signals` (строка 244)
- `eventFilter` (строка 260)
- `changeEvent` (строка 273)
- `_on_input_changed` (строка 295)
- `_on_send_message` (строка 302)
- `add_message` (строка 321)
- `clear_input` (строка 347)
- `get_input_text` (строка 351)
- `_on_attach_file` (строка 355)
- `_on_attach_image` (строка 362)

### agent\reflection_agent.py (10 заглушек)

- `_create_error_reflection_result` (строка 299)
- `_extract_issues_and_recommendations` (строка 326)
- `_determine_problem_type` (строка 417)
- `_split_text_into_sections` (строка 440)
- `_extract_items_from_section` (строка 490)
- `_extract_recommendations_from_text` (строка 529)
- `_extract_issues_from_text` (строка 576)
- `_extract_confidence_score` (строка 617)
- `_extract_summary` (строка 678)
- `_get_strategy_description` (строка 832)

### pocketflow\fixed_orchestrator.py (10 заглушек)

- `run` (строка 28)
- `register_tool` (строка 56)
- `register_agent` (строка 66)
- `register_flow` (строка 76)
- `create_tool_node` (строка 87)
- `create_agent_node` (строка 104)
- `create_sequential_workflow` (строка 121)
- `create_branching_workflow` (строка 154)
- `create_agent_workflow` (строка 204)
- `run_workflow` (строка 255)

### utils\error_handling.py (10 заглушек)

- `log_exception` (строка 113)
- `handle_exception` (строка 131)
- `convert_exception` (строка 161)
- `catch_all` (строка 198)
- `retry_on_exception` (строка 226)
- `set_global_exception_handler` (строка 286)
- `format_exception_for_user` (строка 312)
- `get_error_details` (строка 333)
- `is_critical_error` (строка 357)
- `create_error_report` (строка 381)

### ui\utils\css_tools\css_refactor.py (9 заглушек)

- `find_duplicate_selectors` (строка 31)
- `extract_colors` (строка 52)
- `create_color_variables` (строка 70)
- `replace_colors_with_variables` (строка 95)
- `merge_duplicate_selectors` (строка 111)
- `fix_duplicate_selectors` (строка 154)
- `fix_hardcoded_colors` (строка 190)
- `create_theme_definitions` (строка 232)
- `main` (строка 267)

### ui\utils\css_tools\fix_duplicate_selectors.py (9 заглушек)

- `read_file` (строка 19)
- `write_file` (строка 24)
- `extract_style_blocks` (строка 29)
- `find_duplicate_selectors` (строка 35)
- `group_by_base_selector` (строка 59)
- `parse_properties` (строка 77)
- `merge_duplicate_selectors` (строка 91)
- `fix_file` (строка 140)
- `main` (строка 166)

### ui\utils\css_tools\css_fixer.py (8 заглушек)

- `read_file` (строка 17)
- `write_file` (строка 22)
- `extract_css_blocks` (строка 27)
- `parse_properties` (строка 33)
- `find_duplicate_selectors` (строка 47)
- `rebuild_css` (строка 72)
- `fix_css_file` (строка 108)
- `main` (строка 147)

### agent\planning_strategy.py (7 заглушек)

- `_determine_complexity_by_thresholds` (строка 164)
- `_parse_complexity_metadata` (строка 187)
- `_extract_json_from_text` (строка 377)
- `_extract_numerical_score` (строка 561)
- `_extract_numerical_score` (строка 745)
- `_extract_numerical_score` (строка 921)
- `get_planning_strategy` (строка 986)

### marketing\fixed_orchestrator.py (7 заглушек)

- `run` (строка 36)
- `create_content_planning_workflow` (строка 69)
- `create_content_creation_workflow` (строка 106)
- `create_content_distribution_workflow` (строка 141)
- `create_content_analytics_workflow` (строка 179)
- `create_end_to_end_marketing_workflow` (строка 202)
- `register_pocketflow` (строка 261)

### pocketflow\orchestrator.py (7 заглушек)

- `register_agent` (строка 51)
- `register_tool` (строка 57)
- `register_pocketflow` (строка 63)
- `register_flow` (строка 69)
- `create_planning_workflow` (строка 75)
- `create_agent_workflow` (строка 111)
- `create_hybrid_workflow` (строка 147)

### ui\utils\css_tools\theme_compiler.py (7 заглушек)

- `find_theme_files` (строка 23)
- `compile_theme` (строка 53)
- `fix_qss_paths` (строка 104)
- `fix_resource_path` (строка 141)
- `compile_all_themes` (строка 169)
- `generate_theme_vars` (строка 218)
- `main` (строка 253)

### marketing\tools.py (6 заглушек)

- `execute` (строка 26)
- `execute` (строка 40)
- `execute` (строка 103)
- `execute` (строка 212)
- `execute` (строка 282)
- `execute` (строка 328)

### pocketflow\core.py (6 заглушек)

- `connect` (строка 72)
- `prep` (строка 99)
- `exec` (строка 110)
- `post` (строка 121)
- `connect` (строка 150)
- `run` (строка 165)

### ui\utils\css_tools\cleanup.py (6 заглушек)

- `cleanup_files` (строка 46)
- `handle_special_files` (строка 87)
- `is_newer_theme_manager` (строка 130)
- `backup_and_update_file` (строка 147)
- `find_temp_files` (строка 168)
- `main` (строка 195)

### marketing\orchestrator.py (5 заглушек)

- `create_content_planning_workflow` (строка 50)
- `create_content_creation_workflow` (строка 87)
- `create_content_distribution_workflow` (строка 128)
- `create_content_analytics_workflow` (строка 168)
- `create_end_to_end_marketing_workflow` (строка 199)

### ui\styles.py (5 заглушек)

- `load_fonts` (строка 12)
- `apply_default_font` (строка 69)
- `load_qss_file` (строка 102)
- `update_styles` (строка 123)
- `load_styles` (строка 157)

### utils\ui_utils.py (5 заглушек)

- `load_fonts` (строка 8)
- `validate_ui_components` (строка 43)
- `apply_dock_constraints` (строка 60)
- `update_custom_title_bars` (строка 74)
- `fix_duplicate_docks` (строка 87)

### logic\agent_setup.py (4 заглушек)

- `handle_agent_response` (строка 22)
- `update_agent_status_display` (строка 33)
- `setup_agent` (строка 39)
- `connect_agent_signals` (строка 82)

### logic\event_handlers.py (4 заглушек)

- `on_file_double_clicked` (строка 6)
- `on_tab_changed` (строка 18)
- `on_project_tree_double_clicked` (строка 33)
- `on_dock_visibility_changed` (строка 53)

### ui\main_window.py (4 заглушек)

- `_setup_ui` (строка 98)
- `_connect_global_ui_signals` (строка 172)
- `_apply_initial_layout` (строка 194)
- `_update_view_menu` (строка 234)

### ui\terminal_widget.py (4 заглушек)

- `_setup_ui` (строка 58)
- `eventFilter` (строка 101)
- `_connect_signals` (строка 114)
- `_process_command` (строка 119)

### ui\utils\css_tools\fonts_fixer.py (4 заглушек)

- `extract_font_faces` (строка 15)
- `parse_font_face` (строка 19)
- `normalize_font_faces` (строка 37)
- `main` (строка 100)

### ui\utils\css_tools\simple_ui_auditor_final.py (4 заглушек)

- `run_audit_cli` (строка 387)
- `analyze_python_files_cli` (строка 492)
- `analyze_qss_files_cli` (строка 538)
- `analyze_ui_files_cli` (строка 603)

### pocketflow\adapters.py (3 заглушек)

- `prep` (строка 87)
- `exec` (строка 97)
- `post` (строка 160)

### ui\browser_widget.py (3 заглушек)

- `initialize_cef` (строка 426)
- `shutdown_cef` (строка 451)
- `get_browser_widget` (строка 462)

### ui\i18n\compile_translations.py (3 заглушек)

- `ensure_en_us_translation` (строка 32)
- `fix_translation_file` (строка 64)
- `compile_translations` (строка 77)

### ui\i18n\translator.py (3 заглушек)

- `tr` (строка 289)
- `check_translator` (строка 293)
- `connect_language_actions` (строка 346)

### icons_rc.py (2 заглушек)

- `qInitResources` (строка 419)
- `qCleanupResources` (строка 422)

### flow\base.py (2 заглушек)

- `get_agent` (строка 78)
- `add_agent` (строка 91)

### tool\browser_tools_integration.py (2 заглушек)

- `initialize_browser_tools` (строка 68)
- `get_browser_tools` (строка 79)

### tool\code_tools_integration.py (2 заглушек)

- `initialize_coding_tools` (строка 77)
- `get_coding_tools` (строка 91)

### ui\code_analysis_integration.py (2 заглушек)

- `integrate_with_main_window` (строка 13)
- `open_code_analysis_widget` (строка 61)

### ui\docks.py (2 заглушек)

- `create_docks` (строка 13)
- `_connect_editor_chat_signals` (строка 76)

### utils\theme_utils.py (2 заглушек)

- `get_additional_qss_template` (строка 6)
- `on_theme_changed_event` (строка 189)

### utils\translation.py (2 заглушек)

- `translate` (строка 8)
- `on_language_changed_event` (строка 11)

### config.py (1 заглушек)

- `get_project_root` (строка 30)

### llm.py (1 заглушек)

- `get_llm_client` (строка 774)

### logger.py (1 заглушек)

- `define_log_level` (строка 9)

### agent\metacognitive_analyzer.py (1 заглушек)

- `_extract_metrics_and_recommendations` (строка 248)

### mcp\sequential_thinking.py (1 заглушек)

- `is_available` (строка 56)

### mcp\server.py (1 заглушек)

- `parse_args` (строка 241)

### sandbox\client.py (1 заглушек)

- `create_sandbox_client` (строка 191)

### sandbox\core\manager.py (1 заглушек)

- `start_cleanup_task` (строка 173)

### tool\base.py (1 заглушек)

- `to_dict` (строка 52)

### tool\str_replace_editor.py (1 заглушек)

- `maybe_truncate` (строка 49)

### tool\search\test_ddg.py (1 заглушек)

- `test_search` (строка 2)

### ui\browser_tab_widget.py (1 заглушек)

- `generate_browser_qss` (строка 16)

### ui\central_widget.py (1 заглушек)

- `setup_central_widget` (строка 6)

### ui\debug_ui.py (1 заглушек)

- `run_ui_diagnostics` (строка 290)

### ui\dock_title_bar.py (1 заглушек)

- `apply_custom_title_bar` (строка 222)

### ui\flow_visualizer.py (1 заглушек)

- `show_flow_visualizer_dialog` (строка 275)

### ui\menus.py (1 заглушек)

- `setup_menus` (строка 10)

### ui\status_bar.py (1 заглушек)

- `create_status_bar` (строка 4)

### ui\syntax_highlighter.py (1 заглушек)

- `format` (строка 4)

### ui\toolbars.py (1 заглушек)

- `create_toolbars` (строка 3)

### ui\utils\css_tools\compile_themes.py (1 заглушек)

- `main` (строка 25)

### utils\settings.py (1 заглушек)

- `restore_window_state` (строка 6)

### utils\signal_checker.py (1 заглушек)

- `auto_connect_signals` (строка 326)
