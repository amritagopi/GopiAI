# GopiAI Test Suite Documentation

Generated on: 2025-08-10 13:18:07

## Overview

This document provides comprehensive documentation for the GopiAI Test Suite.
The test suite contains **842 tests** across **60 modules**.
Estimated total runtime: **slow (>30m)**

## Test Statistics

| Metric | Value |
|--------|-------|
| Total Tests | 842 |
| Total Modules | 60 |
| Total Fixtures | 6 |
| Estimated Runtime | slow (>30m) |

### Tests by Category

| Category | Count | Percentage |
|----------|-------|------------|
| E2E | 14 | 1.7% |
| Integration | 131 | 15.6% |
| Performance | 43 | 5.1% |
| Security | 30 | 3.6% |
| Ui | 172 | 20.4% |
| Unit | 452 | 53.7% |
| Unknown | 0 | 0.0% |

## Test Modules

### test_terminal_tool

**File:** `GopiAI-CrewAI\tests\e2e\test_terminal_tool.py`
**Category:** E2E
**Tests:** 2
**Estimated Runtime:** fast (<30s)

#### Test Functions

| Function | Complexity | Runtime | Markers |
|----------|------------|---------|---------|
| `test_terminal_tool_pwd_unsafe_mode` | medium | fast (<5s) | none |
| `test_terminal_tool_echo_windows` | medium | fast (<5s) | none |

---

### test_complete_scenarios

**File:** `tests\e2e\test_complete_scenarios.py`
**Category:** E2E
**Tests:** 12
**Estimated Runtime:** medium (30s-5m)

**Description:**
Comprehensive End-to-End Tests for GopiAI System

Tests complete user scenarios from UI interaction through backend processing
to AI response and memory persistence.

#### Test Classes

**TestCompleteConversationFlow**
- Test complete conversation flow from start to finish.
- Methods: 3

**TestMemoryPersistence**
- Test memory persistence across sessions.
- Methods: 3

**TestServiceRecovery**
- Test system recovery after service failures.
- Methods: 3

**TestMultipleUsers**
- Test system behavior with multiple concurrent users.
- Methods: 3

#### Fixtures

- `e2e_environment`

---

### test_runner_e2e

**File:** `tests\e2e\test_runner_e2e.py`
**Category:** E2E
**Tests:** 0
**Estimated Runtime:** 0s

**Description:**
End-to-End Test Runner for GopiAI System

Specialized test runner for E2E tests with proper service management
and environment setup.

---

### test_asset_integration

**File:** `GopiAI-Assets\tests\integration\test_asset_integration.py`
**Category:** Integration
**Tests:** 2
**Estimated Runtime:** fast (<30s)

**Description:**
Integration tests for GopiAI-Assets module.

Tests integration between asset management and other GopiAI components.

#### Test Classes

**TestAssetIntegration**
- Test asset integration with other components.
- Methods: 2

---

### test_core_integration

**File:** `GopiAI-Core\tests\integration\test_core_integration.py`
**Category:** Integration
**Tests:** 3
**Estimated Runtime:** fast (<30s)

**Description:**
Integration tests for GopiAI-Core module.

Tests integration between core components and other GopiAI modules.

#### Test Classes

**TestCoreIntegration**
- Test core component integration.
- Methods: 3

---

### test_api_endpoints

**File:** `GopiAI-CrewAI\tests\integration\test_api_endpoints.py`
**Category:** Integration
**Tests:** 36
**Estimated Runtime:** medium (30s-5m)

**Description:**
Integration Tests for CrewAI API Endpoints

Tests all REST endpoints of the CrewAI server to ensure proper functionality,
error handling, and integration with external services.

Requirements covered:
- 2.1: API endpoint testing
- 2.2: Service integration testing  
- 7.1: API security testing

#### Test Classes

**TestAPIEndpoints**
- Test all CrewAI API endpoints.
- Methods: 0

**TestHealthEndpoint**
- Test /api/health endpoint.
- Methods: 3

**TestProcessEndpoint**
- Test /api/process endpoint.
- Methods: 6

**TestTaskEndpoint**
- Test /api/task/<task_id> endpoint.
- Methods: 3

**TestDebugEndpoint**
- Test /api/debug endpoint.
- Methods: 1

**TestInternalEndpoints**
- Test internal API endpoints.
- Methods: 5

**TestToolsEndpoints**
- Test tools management endpoints.
- Methods: 5

**TestAgentsEndpoint**
- Test agents management endpoint.
- Methods: 1

**TestSettingsEndpoints**
- Test settings management endpoints.
- Methods: 3

**TestErrorHandling**
- Test API error handling.
- Methods: 3

**TestConcurrentRequests**
- Test concurrent request handling.
- Methods: 2

**TestSecurityAspects**
- Test security aspects of the API.
- Methods: 4

---

### test_authentication

**File:** `GopiAI-CrewAI\tests\integration\test_authentication.py`
**Category:** Integration
**Tests:** 16
**Estimated Runtime:** medium (30s-5m)

**Description:**
Integration Tests for Authentication and Authorization

Tests authentication mechanisms, API key validation, and access control
for the CrewAI API server.

Requirements covered:
- 2.2: Authentication and authorization testing
- 7.1: API security testing

#### Test Classes

**TestAuthentication**
- Test authentication and authorization mechanisms.
- Methods: 0

**TestAPIKeyValidation**
- Test API key validation and management.
- Methods: 4

**TestAccessControl**
- Test access control and authorization.
- Methods: 4

**TestSecureHeaders**
- Test security headers in responses.
- Methods: 3

**TestSessionManagement**
- Test session management and state handling.
- Methods: 2

**TestInputValidation**
- Test input validation and sanitization.
- Methods: 3

---

### test_error_handling

**File:** `GopiAI-CrewAI\tests\integration\test_error_handling.py`
**Category:** Integration
**Tests:** 24
**Estimated Runtime:** medium (30s-5m)

**Description:**
Integration Tests for API Error Handling

Tests error handling, recovery mechanisms, and graceful degradation
for the CrewAI API server.

Requirements covered:
- 2.1: API error handling testing
- 2.2: Service integration error handling
- 7.1: API security error handling

#### Test Classes

**TestAPIErrorHandling**
- Test API error handling and recovery mechanisms.
- Methods: 0

**TestHTTPErrorHandling**
- Test HTTP-level error handling.
- Methods: 6

**TestServiceErrorHandling**
- Test service-level error handling.
- Methods: 4

**TestDataValidationErrors**
- Test data validation error handling.
- Methods: 4

**TestSecurityErrorHandling**
- Test security-related error handling.
- Methods: 3

**TestRecoveryMechanisms**
- Test system recovery mechanisms.
- Methods: 4

**TestErrorResponseFormat**
- Test error response format consistency.
- Methods: 3

---

### test_external_ai_services

**File:** `GopiAI-CrewAI\tests\integration\test_external_ai_services.py`
**Category:** Integration
**Tests:** 21
**Estimated Runtime:** medium (30s-5m)

**Description:**
Integration Tests for External AI Services

Tests integration with external AI services (OpenAI, Anthropic, Google, etc.)
including authentication, rate limiting, and error handling.

Requirements covered:
- 2.2: External service integration testing
- 7.1: API security with external services

#### Test Classes

**TestExternalAIServices**
- Test integration with external AI services.
- Methods: 0

**TestOpenAIIntegration**
- Test OpenAI service integration.
- Methods: 4

**TestAnthropicIntegration**
- Test Anthropic (Claude) service integration.
- Methods: 3

**TestGoogleAIIntegration**
- Test Google AI (Gemini) service integration.
- Methods: 3

**TestOpenRouterIntegration**
- Test OpenRouter service integration.
- Methods: 2

**TestProviderSwitching**
- Test switching between AI providers.
- Methods: 4

**TestServiceResilience**
- Test resilience to external service issues.
- Methods: 5

---

### test_runner

**File:** `GopiAI-CrewAI\tests\integration\test_runner.py`
**Category:** Integration
**Tests:** 0
**Estimated Runtime:** 0s

**Description:**
Integration Test Runner

Comprehensive test runner for all CrewAI API integration tests.
Manages test execution order, service dependencies, and reporting.

Requirements covered:
- 2.1: API integration testing coordination
- 2.2: Service integration testing management
- 7.1: Security testing coordination

---

### test_setup_verification

**File:** `GopiAI-CrewAI\tests\integration\test_setup_verification.py`
**Category:** Integration
**Tests:** 6
**Estimated Runtime:** fast (<30s)

**Description:**
Integration Test Setup Verification

Simple test to verify that the integration test infrastructure is working correctly.

#### Test Classes

**TestSetupVerification**
- Verify integration test setup is working.
- Methods: 6

---

### test_txtai_integration

**File:** `tests\memory\test_txtai_integration.py`
**Category:** Integration
**Tests:** 23
**Estimated Runtime:** medium (30s-5m)

**Description:**
Txtai Integration Tests for GopiAI Memory System

Specific tests for txtai indexing, embedding generation, and search functionality.
Part of task 8: Реализовать тесты системы памяти.

#### Test Classes

**TestTxtaiIndexing**
- Test txtai indexing functionality.
- Methods: 7

**TestTxtaiSearch**
- Test txtai search functionality.
- Methods: 5

**TestTxtaiPerformance**
- Test txtai performance characteristics.
- Methods: 3

**TestTxtaiIntegration**
- Test txtai integration with GopiAI memory system.
- Methods: 4

**TestTxtaiErrorHandling**
- Test txtai error handling and edge cases.
- Methods: 4

---

### test_api_performance

**File:** `GopiAI-CrewAI\tests\performance\test_api_performance.py`
**Category:** Performance
**Tests:** 5
**Estimated Runtime:** fast (<30s)

**Description:**
Performance tests for GopiAI-CrewAI module.

Tests API performance, response times, and throughput.

#### Test Classes

**TestAPIPerformance**
- Test API performance characteristics.
- Methods: 3

**TestMemoryPerformance**
- Test memory system performance.
- Methods: 2

---

### test_search_performance

**File:** `tests\memory\test_search_performance.py`
**Category:** Performance
**Tests:** 15
**Estimated Runtime:** medium (30s-5m)

**Description:**
Memory Search Performance Tests for GopiAI Memory System

Tests for search performance, indexing speed, and scalability.
Part of task 8: Реализовать тесты системы памяти.

#### Test Classes

**TestSearchPerformanceBasic**
- Test basic search performance characteristics.
- Methods: 5

**TestConcurrentSearchPerformance**
- Test search performance under concurrent load.
- Methods: 3

**TestIndexingPerformance**
- Test indexing and reindexing performance.
- Methods: 4

**TestMemoryUsagePerformance**
- Test memory usage characteristics during search operations.
- Methods: 3

---

### test_api_benchmarks

**File:** `tests\performance\test_api_benchmarks.py`
**Category:** Performance
**Tests:** 6
**Estimated Runtime:** fast (<30s)

**Description:**
API performance benchmarks for CrewAI server endpoints.

#### Test Classes

**TestAPIPerformance**
- API performance tests.
- Methods: 6

#### Fixtures

- `api_benchmark`

---

### test_memory_performance

**File:** `tests\performance\test_memory_performance.py`
**Category:** Performance
**Tests:** 9
**Estimated Runtime:** fast (<30s)

**Description:**
Memory system performance tests for txtai integration.

#### Test Functions

| Function | Complexity | Runtime | Markers |
|----------|------------|---------|---------|
| `test_documents` | simple | fast (<5s) | fixture |

#### Test Classes

**TestMemorySystemPerformance**
- Memory system performance tests.
- Methods: 8

#### Fixtures

- `memory_benchmark`

---

### test_runner_performance

**File:** `tests\performance\test_runner_performance.py`
**Category:** Performance
**Tests:** 0
**Estimated Runtime:** 0s

**Description:**
Performance test runner for coordinated execution of all performance tests.

---

### test_system_monitoring

**File:** `tests\performance\test_system_monitoring.py`
**Category:** Performance
**Tests:** 8
**Estimated Runtime:** fast (<30s)

**Description:**
System monitoring and resource usage performance tests.

#### Test Classes

**TestSystemMonitoring**
- System monitoring and resource usage tests.
- Methods: 8

#### Fixtures

- `system_monitor`
- `leak_detector`

---

### test_api_security

**File:** `GopiAI-CrewAI\tests\security\test_api_security.py`
**Category:** Security
**Tests:** 18
**Estimated Runtime:** medium (30s-5m)

**Description:**
Security tests for GopiAI-CrewAI module.

Tests API security, authentication, and protection against common attacks.
Requirements: 7.1, 7.2, 7.3, 7.4

#### Test Classes

**TestAPISecurityBasics**
- Test basic API security measures - Requirement 7.1.
- Methods: 5

**TestSecretManagement**
- Test secret and API key management security - Requirement 7.2.
- Methods: 4

**TestAuthenticationSecurity**
- Test authentication and session security - Requirement 7.3.
- Methods: 3

**TestFileSystemSecurity**
- Test file system operation security - Requirement 7.4.
- Methods: 4

**TestSecurityConfiguration**
- Test security configuration and settings.
- Methods: 2

---

### test_comprehensive_security

**File:** `tests\security\test_comprehensive_security.py`
**Category:** Security
**Tests:** 12
**Estimated Runtime:** medium (30s-5m)

**Description:**
Comprehensive security tests for the entire GopiAI system.

Tests cross-module security, integration security, and system-wide security measures.
Requirements: 7.1, 7.2, 7.3, 7.4

#### Test Classes

**TestSystemWideSecurity**
- Test system-wide security measures across all modules.
- Methods: 4

**TestCommunicationSecurity**
- Test security of inter-module communication.
- Methods: 3

**TestDataProtectionSecurity**
- Test data protection and privacy security measures.
- Methods: 3

**TestSecurityMonitoring**
- Test security monitoring and alerting systems.
- Methods: 2

---

### test_runner_security

**File:** `tests\security\test_runner_security.py`
**Category:** Security
**Tests:** 0
**Estimated Runtime:** 0s

**Description:**
Security test runner for GopiAI comprehensive testing system.

Provides utilities for running security tests with proper configuration and reporting.
Requirements: 7.1, 7.2, 7.3, 7.4

---

### test_user_scenarios

**File:** `GopiAI-UI\tests\e2e\test_user_scenarios.py`
**Category:** Ui
**Tests:** 5
**Estimated Runtime:** fast (<30s)

**Description:**
End-to-end tests for GopiAI-UI module.

Tests complete user scenarios from UI interaction to backend response.
This file now redirects to the comprehensive E2E tests in tests/e2e/

#### Test Classes

**TestUserScenarios**
- Test complete user scenarios - redirects to comprehensive E2E tests.
- Methods: 5

---

### test_ui_performance

**File:** `GopiAI-UI\tests\performance\test_ui_performance.py`
**Category:** Ui
**Tests:** 3
**Estimated Runtime:** fast (<30s)

**Description:**
Performance tests for GopiAI-UI module.

Tests UI responsiveness and performance under various conditions.

#### Test Classes

**TestUIPerformance**
- Test UI performance characteristics.
- Methods: 3

---

### test_ui_security

**File:** `GopiAI-UI\tests\security\test_ui_security.py`
**Category:** Ui
**Tests:** 13
**Estimated Runtime:** medium (30s-5m)

**Description:**
Security tests for GopiAI-UI module.

Tests UI security, input validation, and protection against client-side attacks.
Requirements: 7.1, 7.2, 7.3, 7.4

#### Test Classes

**TestUIInputSecurity**
- Test UI input validation and sanitization - Requirement 7.1.
- Methods: 3

**TestUISecretManagement**
- Test UI secret and sensitive data handling - Requirement 7.2.
- Methods: 3

**TestUISessionSecurity**
- Test UI session and authentication security - Requirement 7.3.
- Methods: 3

**TestUIFileSystemSecurity**
- Test UI file system operation security - Requirement 7.4.
- Methods: 4

---

### test_chat_widget

**File:** `GopiAI-UI\tests\ui\test_chat_widget.py`
**Category:** Ui
**Tests:** 13
**Estimated Runtime:** medium (30s-5m)

**Description:**
UI tests for chat widget using pytest-qt and improved fixtures.

#### Test Classes

**TestChatWidget**
- Test chat widget functionality.
- Methods: 11

**TestChatWidgetPerformance**
- Performance tests for chat widget.
- Methods: 2

---

### test_file_operations_ui

**File:** `GopiAI-UI\tests\ui\test_file_operations_ui.py`
**Category:** Ui
**Tests:** 29
**Estimated Runtime:** medium (30s-5m)

**Description:**
UI tests for file operations functionality using pytest-qt.
Tests file handling, drag-and-drop, import/export, and file management through UI.

#### Test Classes

**TestFileDialogOperations**
- Test file dialog operations through UI.
- Methods: 4

**TestDragAndDropOperations**
- Test drag and drop file operations.
- Methods: 5

**TestFileImportExport**
- Test file import and export operations.
- Methods: 5

**TestFileAttachmentOperations**
- Test file attachment operations in chat.
- Methods: 6

**TestFileErrorHandling**
- Test error handling for file operations.
- Methods: 4

**TestFileOperationsProgress**
- Test progress indication for file operations.
- Methods: 3

**TestFileOperationsIntegration**
- Test integration of file operations with other UI components.
- Methods: 2

---

### test_main_window_ui

**File:** `GopiAI-UI\tests\ui\test_main_window_ui.py`
**Category:** Ui
**Tests:** 22
**Estimated Runtime:** medium (30s-5m)

**Description:**
UI tests for main window using pytest-qt.
Tests main user scenarios and window interactions.

#### Test Classes

**TestMainWindowUI**
- Test main window UI functionality.
- Methods: 11

**TestMainWindowFileOperations**
- Test main window file operations.
- Methods: 5

**TestMainWindowSettings**
- Test main window settings functionality.
- Methods: 4

**TestMainWindowPerformance**
- Performance tests for main window.
- Methods: 2

---

### test_message_sending_ui

**File:** `GopiAI-UI\tests\ui\test_message_sending_ui.py`
**Category:** Ui
**Tests:** 22
**Estimated Runtime:** medium (30s-5m)

**Description:**
UI tests for message sending and receiving functionality using pytest-qt.
Tests the core message sending scenarios and user interactions.

#### Test Classes

**TestMessageSendingUI**
- Test message sending functionality through UI.
- Methods: 11

**TestMessageReceivingUI**
- Test message receiving functionality through UI.
- Methods: 5

**TestMessageUIIntegration**
- Test integration between message sending and UI components.
- Methods: 4

**TestMessageSendingPerformance**
- Performance tests for message sending UI.
- Methods: 2

---

### test_model_switching_ui

**File:** `GopiAI-UI\tests\ui\test_model_switching_ui.py`
**Category:** Ui
**Tests:** 22
**Estimated Runtime:** medium (30s-5m)

**Description:**
UI tests for model switching functionality using pytest-qt.
Tests model selection, switching, and integration with chat functionality.

#### Test Classes

**TestModelSelectorUI**
- Test model selector widget functionality.
- Methods: 6

**TestModelSwitchingIntegration**
- Test model switching integration with other UI components.
- Methods: 4

**TestModelAvailabilityUI**
- Test model availability and status in UI.
- Methods: 3

**TestModelConfigurationUI**
- Test model configuration through UI.
- Methods: 3

**TestModelSwitchingPerformance**
- Test performance aspects of model switching.
- Methods: 2

**TestModelSwitchingKeyboardShortcuts**
- Test keyboard shortcuts for model switching.
- Methods: 2

**TestModelSwitchingFullIntegration**
- Test full integration of model switching with entire UI.
- Methods: 2

---

### test_runner_ui

**File:** `GopiAI-UI\tests\ui\test_runner_ui.py`
**Category:** Ui
**Tests:** 0
**Estimated Runtime:** 0s

**Description:**
UI Test Runner for GopiAI-UI pytest-qt tests.
Coordinates execution of all UI tests and provides comprehensive reporting.

---

### test_settings_ui

**File:** `GopiAI-UI\tests\ui\test_settings_ui.py`
**Category:** Ui
**Tests:** 33
**Estimated Runtime:** medium (30s-5m)

**Description:**
UI tests for settings functionality using pytest-qt.
Tests settings dialog, preferences management, and configuration through UI.

#### Test Classes

**TestSettingsDialogUI**
- Test settings dialog functionality.
- Methods: 5

**TestThemeSettings**
- Test theme-related settings functionality.
- Methods: 4

**TestFontSettings**
- Test font-related settings functionality.
- Methods: 4

**TestAPIKeySettings**
- Test API key management in settings.
- Methods: 4

**TestModelSettings**
- Test model-related settings functionality.
- Methods: 3

**TestBehaviorSettings**
- Test behavior-related settings functionality.
- Methods: 4

**TestSettingsPersistence**
- Test settings persistence functionality.
- Methods: 5

**TestSettingsIntegration**
- Test settings integration with other UI components.
- Methods: 3

**TestSettingsKeyboardShortcuts**
- Test keyboard shortcuts for settings.
- Methods: 1

---

### test_simple_ui

**File:** `GopiAI-UI\tests\ui\test_simple_ui.py`
**Category:** Ui
**Tests:** 2
**Estimated Runtime:** fast (<30s)

**Description:**
Simple UI test to verify pytest-qt setup.

#### Test Classes

**TestSimpleUI**
- Simple UI tests to verify setup.
- Methods: 2

---

### test_ui_performance

**File:** `tests\performance\test_ui_performance.py`
**Category:** Ui
**Tests:** 8
**Estimated Runtime:** fast (<30s)

**Description:**
UI performance tests for PySide6 application responsiveness.

#### Test Classes

**TestUIPerformance**
- UI performance tests.
- Methods: 8

#### Fixtures

- `ui_benchmark`

---

### test_assets

**File:** `GopiAI-Assets\tests\unit\test_assets.py`
**Category:** Unit
**Tests:** 6
**Estimated Runtime:** fast (<30s)

**Description:**
Unit tests for GopiAI-Assets module.

Tests asset loading, management, and validation functionality.

#### Test Classes

**TestAssetManagement**
- Test asset management functionality.
- Methods: 3

**TestAssetTypes**
- Test different types of assets.
- Methods: 3

---

### test_exceptions

**File:** `GopiAI-Core\tests\test_exceptions.py`
**Category:** Unit
**Tests:** 41
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for GopiAI Core Exceptions

Tests the custom exception hierarchy and error handling functionality.

#### Test Classes

**TestGopiAIError**
- Test base GopiAIError exception.
- Methods: 3

**TestConfigurationError**
- Test ConfigurationError exception.
- Methods: 2

**TestAIProviderErrors**
- Test AI provider related exceptions.
- Methods: 4

**TestMemoryErrors**
- Test memory system related exceptions.
- Methods: 3

**TestUIErrors**
- Test UI related exceptions.
- Methods: 3

**TestServiceErrors**
- Test service related exceptions.
- Methods: 3

**TestValidationErrors**
- Test validation related exceptions.
- Methods: 2

**TestToolErrors**
- Test tool related exceptions.
- Methods: 3

**TestSecurityErrors**
- Test security related exceptions.
- Methods: 3

**TestFileSystemErrors**
- Test file system related exceptions.
- Methods: 3

**TestNetworkErrors**
- Test network related exceptions.
- Methods: 3

**TestExceptionUtilities**
- Test exception utility functions.
- Methods: 4

**TestExceptionContextHandling**
- Test exception context handling.
- Methods: 2

**TestKnownExceptionIssues**
- Test known issues with exceptions marked as expected failures.
- Methods: 3

---

### test_interfaces

**File:** `GopiAI-Core\tests\test_interfaces.py`
**Category:** Unit
**Tests:** 21
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for GopiAI Core Interfaces

Tests the abstract base classes and interface definitions.

#### Test Classes

**TestAIProviderInterface**
- Test AIProviderInterface abstract base class.
- Methods: 4

**TestMemoryInterface**
- Test MemoryInterface abstract base class.
- Methods: 3

**TestUIComponentInterface**
- Test UIComponentInterface abstract base class.
- Methods: 2

**TestConfigurationInterface**
- Test ConfigurationInterface abstract base class.
- Methods: 2

**TestToolInterface**
- Test ToolInterface abstract base class.
- Methods: 2

**TestServiceInterface**
- Test ServiceInterface abstract base class.
- Methods: 2

**TestServiceInfo**
- Test ServiceInfo dataclass.
- Methods: 2

**TestInterfaceInheritance**
- Test interface inheritance and ABC behavior.
- Methods: 2

**TestKnownInterfaceIssues**
- Test known issues with interfaces marked as expected failures.
- Methods: 2

---

### test_schema

**File:** `GopiAI-Core\tests\test_schema.py`
**Category:** Unit
**Tests:** 47
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for GopiAI Core Schema

Tests data models, validation schemas, and data structures.

#### Test Classes

**TestEnums**
- Test enumeration classes.
- Methods: 4

**TestMessage**
- Test Message dataclass.
- Methods: 5

**TestConversation**
- Test Conversation dataclass.
- Methods: 4

**TestModelInfo**
- Test ModelInfo dataclass.
- Methods: 2

**TestAPIResponse**
- Test APIResponse dataclass.
- Methods: 3

**TestUsageStats**
- Test UsageStats dataclass.
- Methods: 2

**TestServiceConfig**
- Test ServiceConfig dataclass.
- Methods: 2

**TestToolConfig**
- Test ToolConfig dataclass.
- Methods: 2

**TestUITheme**
- Test UITheme dataclass.
- Methods: 2

**TestMemoryEntry**
- Test MemoryEntry dataclass.
- Methods: 2

**TestSearchResult**
- Test SearchResult dataclass.
- Methods: 2

**TestValidationSchema**
- Test ValidationSchema utility class.
- Methods: 5

**TestConfigSchema**
- Test ConfigSchema validation class.
- Methods: 4

**TestUtilityFunctions**
- Test utility functions.
- Methods: 5

**TestKnownSchemaIssues**
- Test known issues with schema marked as expected failures.
- Methods: 3

---

### test_utils

**File:** `GopiAI-Core\tests\test_utils.py`
**Category:** Unit
**Tests:** 46
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for GopiAI Core Utilities

Tests utility functions used across all GopiAI components.

#### Test Classes

**TestIDGeneration**
- Test ID generation utilities.
- Methods: 3

**TestHashing**
- Test hashing utilities.
- Methods: 3

**TestTimestampUtilities**
- Test timestamp utilities.
- Methods: 3

**TestJSONUtilities**
- Test JSON handling utilities.
- Methods: 4

**TestFileUtilities**
- Test file system utilities.
- Methods: 8

**TestStringUtilities**
- Test string manipulation utilities.
- Methods: 3

**TestDictionaryUtilities**
- Test dictionary manipulation utilities.
- Methods: 7

**TestEnvironmentUtilities**
- Test environment variable utilities.
- Methods: 4

**TestLoggingUtilities**
- Test logging utilities.
- Methods: 2

**TestRetryUtilities**
- Test retry utilities.
- Methods: 3

**TestValidationUtilities**
- Test validation utilities.
- Methods: 3

**TestKnownUtilityIssues**
- Test known issues with utilities marked as expected failures.
- Methods: 3

---

### test_command_processor_improved

**File:** `GopiAI-CrewAI\tests\test_command_processor_improved.py`
**Category:** Unit
**Tests:** 10
**Estimated Runtime:** medium (30s-5m)

**Description:**
Improved tests for command processor using new fixtures.

#### Test Classes

**TestCommandProcessorImproved**
- Improved command processor tests using fixtures.
- Methods: 10

---

### test_command_processor_strict_json

**File:** `GopiAI-CrewAI\tests\test_command_processor_strict_json.py`
**Category:** Unit
**Tests:** 5
**Estimated Runtime:** fast (<30s)

#### Test Classes

**TestCommandProcessorStrictJSON**
- Methods: 5

---

### test_api_server

**File:** `GopiAI-CrewAI\tests\unit\test_api_server.py`
**Category:** Unit
**Tests:** 21
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for CrewAI API Server.

Tests the main API endpoints, request handling, and server functionality.

#### Test Classes

**TestCrewAIAPIServer**
- Test suite for CrewAI API Server endpoints and functionality.
- Methods: 21

---

### test_command_processing

**File:** `GopiAI-CrewAI\tests\unit\test_command_processing.py`
**Category:** Unit
**Tests:** 16
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for Command Processing System.

Tests command extraction, validation, and execution functionality.

#### Test Classes

**TestCommandProcessing**
- Test suite for command processing and tool execution.
- Methods: 16

---

### test_model_switching

**File:** `GopiAI-CrewAI\tests\unit\test_model_switching.py`
**Category:** Unit
**Tests:** 16
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for Model Switching System.

Tests the LLM rotation configuration, model selection, and provider switching.

#### Test Classes

**TestModelSwitching**
- Test suite for model switching and LLM rotation functionality.
- Methods: 16

---

### test_runner

**File:** `GopiAI-CrewAI\tests\unit\test_runner.py`
**Category:** Unit
**Tests:** 0
**Estimated Runtime:** 0s

**Description:**
Unit Test Runner for GopiAI-CrewAI.

Runs all unit tests and provides comprehensive reporting.

#### Test Classes

**TestConfig**
- Simple test configuration class.
- Methods: 0

---

### test_state_manager

**File:** `GopiAI-CrewAI\tests\unit\test_state_manager.py`
**Category:** Unit
**Tests:** 16
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for State Manager.

Tests state persistence, loading, and management functionality.

#### Test Classes

**TestStateManager**
- Test suite for state management functionality.
- Methods: 16

---

### test_main_window

**File:** `GopiAI-UI\tests\unit\test_main_window.py`
**Category:** Unit
**Tests:** 13
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for main window functionality.
Tests the main application window initialization, layout, and basic operations.

#### Test Classes

**TestMainWindow**
- Test main application window functionality.
- Methods: 11

**TestMainWindowErrorHandling**
- Test main window error handling.
- Methods: 2

---

### test_model_selector

**File:** `GopiAI-UI\tests\unit\test_model_selector.py`
**Category:** Unit
**Tests:** 24
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for model selector widget functionality.
Tests model selection, provider switching, and API key management.

#### Test Classes

**TestModelSelector**
- Test model selector widget functionality.
- Methods: 10

**TestModelSelectorAdvanced**
- Test advanced model selector functionality.
- Methods: 7

**TestModelSelectorErrorHandling**
- Test model selector error handling.
- Methods: 4

**TestModelSelectorIntegration**
- Test model selector integration with other components.
- Methods: 3

---

### test_notification_system

**File:** `GopiAI-UI\tests\unit\test_notification_system.py`
**Category:** Unit
**Tests:** 30
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for notification system functionality.
Tests notification display, queuing, persistence, and user interactions.

#### Test Classes

**TestNotificationSystem**
- Test notification system functionality.
- Methods: 10

**TestNotificationQueue**
- Test notification queue functionality.
- Methods: 4

**TestSystemTrayNotifications**
- Test system tray notification functionality.
- Methods: 5

**TestNotificationSettings**
- Test notification settings and preferences.
- Methods: 4

**TestNotificationErrorHandling**
- Test notification system error handling.
- Methods: 4

**TestNotificationIntegration**
- Test notification system integration with other components.
- Methods: 3

---

### test_runner

**File:** `GopiAI-UI\tests\unit\test_runner.py`
**Category:** Unit
**Tests:** 0
**Estimated Runtime:** 0s

**Description:**
Unit Test Runner for GopiAI-UI

Comprehensive test runner for all UI unit tests.
Provides organized test execution, reporting, and error handling.

---

### test_settings_dialog

**File:** `GopiAI-UI\tests\unit\test_settings_dialog.py`
**Category:** Unit
**Tests:** 20
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for settings dialog functionality.
Tests settings dialog initialization, configuration management, and user interactions.

#### Test Classes

**TestSettingsDialog**
- Test settings dialog functionality.
- Methods: 11

**TestSettingsDialogAdvanced**
- Test advanced settings dialog functionality.
- Methods: 5

**TestSettingsDialogErrorHandling**
- Test settings dialog error handling.
- Methods: 3

**TestSettingsDialogIntegration**
- Test settings dialog integration with other components.
- Methods: 1

---

### test_theme_manager

**File:** `GopiAI-UI\tests\unit\test_theme_manager.py`
**Category:** Unit
**Tests:** 17
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for theme manager functionality.
Tests theme switching, theme application, and theme persistence.

#### Test Classes

**TestThemeManager**
- Test theme manager functionality.
- Methods: 11

**TestThemeManagerIntegration**
- Test theme manager integration with other components.
- Methods: 3

**TestThemeManagerErrorHandling**
- Test theme manager error handling.
- Methods: 3

---

### test_user_input_handling

**File:** `GopiAI-UI\tests\unit\test_user_input_handling.py`
**Category:** Unit
**Tests:** 29
**Estimated Runtime:** medium (30s-5m)

**Description:**
Unit tests for user input handling functionality.
Tests keyboard input, mouse interactions, drag and drop, and input validation.

#### Test Classes

**TestUserInputHandling**
- Test user input handling functionality.
- Methods: 10

**TestDragAndDropHandling**
- Test drag and drop functionality.
- Methods: 6

**TestMouseInteractions**
- Test mouse interaction handling.
- Methods: 4

**TestInputValidationAndSanitization**
- Test input validation and sanitization.
- Methods: 4

**TestInputErrorHandling**
- Test input error handling.
- Methods: 3

**TestInputIntegration**
- Test input handling integration with other components.
- Methods: 2

---

### test_discovery

**File:** `test_infrastructure\test_discovery.py`
**Category:** Unit
**Tests:** 0
**Estimated Runtime:** 0s

**Description:**
Test Discovery System for GopiAI Testing Infrastructure

This module discovers and categorizes tests across all GopiAI modules,
providing a unified interface for test execution and reporting.

#### Test Classes

**TestCategory**
- Categories of tests that can be discovered.
- Methods: 0

**TestEnvironment**
- Test environments for GopiAI modules.
- Methods: 0

**TestModule**
- Represents a discovered test module.
- Methods: 0

**TestSuite**
- Represents a collection of test modules.
- Methods: 0

**TestDiscovery**
- Discovers and categorizes tests across GopiAI modules.
- Methods: 0

---

### test_documentation_generator

**File:** `test_infrastructure\test_documentation_generator.py`
**Category:** Unit
**Tests:** 0
**Estimated Runtime:** 0s

**Description:**
Automated Test Documentation Generator

This module automatically generates comprehensive documentation for the GopiAI testing system
by analyzing test files, extracting metadata, and creating formatted documentation.

#### Test Classes

**TestFunction**
- Represents a single test function.
- Methods: 0

**TestClass**
- Represents a test class.
- Methods: 0

**TestModule**
- Represents a test module/file.
- Methods: 0

**TestSuite**
- Represents a complete test suite.
- Methods: 0

**TestDocumentationGenerator**
- Generates comprehensive documentation for test suites.
- Methods: 0

---

### test_fixtures

**File:** `test_infrastructure\test_fixtures.py`
**Category:** Unit
**Tests:** 13
**Estimated Runtime:** medium (30s-5m)

**Description:**
Test the improved fixtures to ensure they work correctly.

#### Test Functions

| Function | Complexity | Runtime | Markers |
|----------|------------|---------|---------|
| `test_ai_service_mocker` | simple | fast (<5s) | none |
| `test_mock_crewai_server` | simple | fast (<5s) | none |
| `test_mock_txtai_memory` | medium | fast (<5s) | none |
| `test_mock_pyside6_app` | simple | fast (<5s) | none |
| `test_mock_gopiai_widgets` | simple | fast (<5s) | none |
| `test_mock_model_config_manager` | simple | fast (<5s) | none |
| `test_mock_usage_tracker` | simple | fast (<5s) | none |
| `test_mock_conversation_manager` | simple | fast (<5s) | none |
| `test_mock_settings_manager` | simple | fast (<5s) | none |
| `test_mock_tool_manager` | simple | fast (<5s) | none |
| `test_sample_conversation` | simple | fast (<5s) | none |
| `test_mock_database` | medium | fast (<5s) | none |
| `test_fixtures_integration` | simple | fast (<5s) | none |

---

### test_service_manager

**File:** `test_infrastructure\test_service_manager.py`
**Category:** Unit
**Tests:** 0
**Estimated Runtime:** 0s

---

### test_conversation_storage

**File:** `tests\memory\test_conversation_storage.py`
**Category:** Unit
**Tests:** 22
**Estimated Runtime:** medium (30s-5m)

**Description:**
Conversation Storage Tests for GopiAI Memory System

Tests for conversation storage, retrieval, and context management.
Part of task 8: Реализовать тесты системы памяти.

#### Test Classes

**TestConversationStorage**
- Test conversation storage functionality.
- Methods: 6

**TestConversationRetrieval**
- Test conversation retrieval functionality.
- Methods: 5

**TestConversationPersistence**
- Test conversation persistence to storage.
- Methods: 4

**TestConversationSearch**
- Test searching within conversations.
- Methods: 4

**TestConversationPerformance**
- Test conversation storage and retrieval performance.
- Methods: 3

---

### test_data_migration

**File:** `tests\memory\test_data_migration.py`
**Category:** Unit
**Tests:** 11
**Estimated Runtime:** medium (30s-5m)

**Description:**
Data Migration Tests for GopiAI Memory System

Tests for data migration between versions, format conversion, and data integrity.
Part of task 8: Реализовать тесты системы памяти.

#### Test Classes

**TestDataMigrationBasic**
- Test basic data migration functionality.
- Methods: 4

**TestVersionCompatibility**
- Test compatibility between different memory format versions.
- Methods: 3

**TestMigrationPerformance**
- Test migration performance with large datasets.
- Methods: 2

**TestMigrationIntegrity**
- Test data integrity during migration.
- Methods: 2

---

### test_memory_system

**File:** `tests\memory\test_memory_system.py`
**Category:** Unit
**Tests:** 28
**Estimated Runtime:** medium (30s-5m)

**Description:**
Memory System Tests for GopiAI

Tests for txtai indexing, search, conversation storage, and data migration.
Covers Requirements 2.3 and 6.2 from the comprehensive testing system spec.

#### Test Classes

**TestTxtaiIndexing**
- Test txtai indexing functionality.
- Methods: 4

**TestMemorySearch**
- Test memory search functionality.
- Methods: 6

**TestConversationStorage**
- Test conversation storage and retrieval.
- Methods: 5

**TestMemoryPerformance**
- Test memory system performance.
- Methods: 6

**TestDataMigration**
- Test data migration between versions.
- Methods: 4

**TestMemorySystemIntegration**
- Integration tests for memory system components.
- Methods: 3

---

### test_config

**File:** `test_infrastructure\test_config.py`
**Category:** Unknown
**Tests:** 0
**Estimated Runtime:** unknown

**Description:**
Error parsing file: unexpected indent (<unknown>, line 247)

---

## Test Fixtures

This section documents all available test fixtures.

| Fixture Name | Module | Description |
|--------------|--------|-------------|
| `api_benchmark` | test_api_benchmarks | Auto-detected fixture |
| `e2e_environment` | test_complete_scenarios | Auto-detected fixture |
| `leak_detector` | test_system_monitoring | Auto-detected fixture |
| `memory_benchmark` | test_memory_performance | Auto-detected fixture |
| `system_monitor` | test_system_monitoring | Auto-detected fixture |
| `ui_benchmark` | test_ui_performance | Auto-detected fixture |

## Running Tests

### Run All Tests
```bash
python run_all_tests.py
```

### Run by Category
```bash
pytest -m e2e
```
```bash
pytest -m integration
```
```bash
pytest -m performance
```
```bash
pytest -m security
```
```bash
pytest -m ui
```
```bash
pytest -m unit
```
```bash
pytest -m unknown
```

### Run Specific Modules
```bash
pytest GopiAI-Assets\tests\integration\test_asset_integration.py
```
```bash
pytest GopiAI-Assets\tests\unit\test_assets.py
```
```bash
pytest GopiAI-Core\tests\integration\test_core_integration.py
```
```bash
pytest GopiAI-Core\tests\test_exceptions.py
```
```bash
pytest GopiAI-Core\tests\test_interfaces.py
```

## Troubleshooting

For common issues and solutions, see:
- [Test Troubleshooting Guide](TEST_TROUBLESHOOTING_GUIDE.md)
- [Testing System Guide](TESTING_SYSTEM_GUIDE.md)
- [Adding New Tests Guide](ADDING_NEW_TESTS_GUIDE.md)
