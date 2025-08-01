# Implementation Plan: GopiAI System Fixes

## Backend Tool System Overhaul

- [x] 1. Remove broken text parsing system






  - Locate and remove regex-based command parsing (`lss*([^n]*)` patterns)
  - Delete functions like `parse_command_from_text()`, `extract_commands()`
  - Remove all `[PARSER]` logging statements
  - Clean up imports related to text parsing
  - _Requirements: 1.1, 1.4_

- [x] 2. Create OpenAI-compatible tool schema




  - Create `tools/gopiai_integration/tool_definitions.py`
  - Implement `get_tool_schema()` function with standard OpenAI format
  - Define schemas for: execute_terminal_command, browse_website, web_search, file_operations
  - Add helper functions: `get_tool_by_name()`, `get_available_tools()`
  - Write unit tests for schema validation
  - _Requirements: 1.1, 1.5_

- [x] 3. Implement native Tool Calling in LLM integration






























  - Modify `smart_delegator.py` to use `litellm.completion()` with `tools` parameter
  - Implement `_call_llm_with_tools()` method with proper tool_calls handling
  - Add two-phase processing: tool execution → final response generation
  - Implement tool call iteration limits to prevent infinite loops
  - Add JSON parsing for tool arguments with error handling
  - _Requirements: 1.1, 1.2, 7.1_

- [-] 4. Rewrite CommandExecutor with direct method interface




  - Replace text parsing with direct method calls: `execute_terminal_command()`, `browse_website()`, etc.
  - Implement command safety validation with whitelist of allowed commands
  - Add timeout handling for command execution (30 second limit)
  - Implement proper error handling and logging for each tool method
  - Add working directory support for terminal commands
  - _Requirements: 1.3, 5.1, 5.2, 5.3, 5.4_

## Error Handling and Resilience

- [ ] 5. Implement comprehensive LLM error handling
  - Add imports for all litellm exception types (RateLimitError, AuthenticationError, etc.)
  - Create retry decorator with exponential backoff for rate limits
  - Implement specific error handling for each exception type
  - Add validation for empty or invalid LLM responses
  - Create structured error response format for API
  - _Requirements: 2.1, 2.2, 2.5_

- [ ] 6. Add tool execution error handling
  - Wrap all tool method calls in try-catch blocks
  - Implement graceful degradation when tools fail
  - Add specific error messages for common failure scenarios
  - Log all tool execution errors with full context
  - Return structured error information in tool results
  - _Requirements: 2.3, 2.5_

- [ ] 7. Create API error response standardization
  - Define consistent JSON response format for all API endpoints
  - Implement error code system for different error types
  - Add retry_after field for rate limit errors
  - Include execution_time and model_info in successful responses
  - Create error response builder utility functions
  - _Requirements: 2.5, 4.2, 4.3_

## Frontend Stability and API Integration

- [ ] 8. Create dedicated API client for backend communication
  - Create `gopiai/ui/api/client.py` with GopiAIAPIClient class
  - Implement `send_message()` method for chat requests
  - Add `get_available_models()` and `health_check()` methods
  - Implement connection error handling and retry logic
  - Add request timeout and connection pooling
  - _Requirements: 4.1, 4.2, 4.4_

- [ ] 9. Fix UI component crashes and stability issues
  - Fix notebook tab creation crashes by adding proper error handling
  - Ensure widget references are stored to prevent garbage collection
  - Add fallback mechanisms for failed component initialization
  - Fix terminal widget to open in tabs instead of floating windows
  - Implement proper parent-child widget relationships
  - _Requirements: 3.1, 3.2, 3.5_

- [ ] 10. Enhance tab management with error recovery
  - Add comprehensive error handling to all tab creation methods
  - Implement fallback tab creation when rich text editor fails
  - Fix context menu operations for tab closing (all, left, right)
  - Add proper cleanup when tabs are closed
  - Ensure background image display when no tabs are open
  - _Requirements: 3.3, 3.4_

- [ ] 11. Implement user-friendly error display system
  - Create `gopiai/ui/components/error_display.py` with ErrorDisplayWidget
  - Add methods for displaying different error types (API, connection, tool)
  - Integrate error display into chat interface
  - Show clear error messages instead of empty responses
  - Add retry buttons for recoverable errors
  - _Requirements: 3.5, 2.1, 2.2_

## Tool Implementation and Safety

- [ ] 12. Implement secure terminal command execution
  - Create whitelist of safe commands (ls, dir, pwd, cat, pip, python, git)
  - Add command validation before execution
  - Implement path traversal protection
  - Add resource limits and timeout enforcement
  - Return both stdout and stderr in structured format
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 6.1_

- [ ] 13. Implement web browsing and search tools
  - Create `browse_website()` with requests and BeautifulSoup
  - Add text extraction and HTML cleaning functionality
  - Implement `web_search()` using DuckDuckGo API or similar
  - Add content length limits and truncation
  - Implement proper error handling for network issues
  - _Requirements: 6.2, 6.3, 6.5_

- [ ] 14. Implement safe file system operations
  - Create `file_operations()` method with operation parameter (read, write, list_dir, exists)
  - Add path validation and security checks
  - Implement file size limits and encoding handling
  - Add directory creation and listing functionality
  - Return structured information about files and directories
  - _Requirements: 6.4, 6.5_

## Testing and Validation

- [ ] 15. Create comprehensive backend tests
  - Write unit tests for tool schema validation
  - Test command safety checking with various inputs
  - Create integration tests for LLM tool calling flow
  - Test error handling for all exception types
  - Add API endpoint tests for request/response format
  - _Requirements: All backend requirements_

- [ ] 16. Create frontend component tests
  - Test tab creation and management functionality
  - Test API client communication and error handling
  - Test error display components
  - Create mock backend for isolated frontend testing
  - Test user workflow scenarios
  - _Requirements: All frontend requirements_

- [ ] 17. Perform end-to-end integration testing
  - Test complete user workflows from UI to backend
  - Validate tool execution through API
  - Test error scenarios and recovery
  - Verify proper separation between frontend and backend
  - Test performance under various load conditions
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 7.4_

## Performance and Security

- [ ] 18. Implement performance optimizations
  - Add connection pooling for LLM API calls
  - Implement caching for tool schemas and model lists
  - Add request queuing and rate limiting
  - Optimize large output handling with truncation
  - Implement proper resource cleanup after tool execution
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 19. Add security measures and validation
  - Implement input validation and sanitization for all API endpoints
  - Add logging for security events and suspicious activities
  - Implement file system access restrictions
  - Add rate limiting per client/session
  - Sanitize error messages to prevent information leakage
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 20. Create monitoring and logging system
  - Add comprehensive logging for all tool executions
  - Implement performance metrics collection
  - Add health check endpoints for monitoring
  - Create error rate tracking and alerting
  - Add request/response logging for debugging
  - _Requirements: 2.5, 7.4_

## Final Integration and Deployment

- [ ] 21. Integration testing and bug fixes
  - Test complete system with all components integrated
  - Fix any remaining issues found during integration
  - Validate that all requirements are met
  - Perform load testing and performance validation
  - Update documentation and deployment guides
  - _Requirements: All requirements_

- [ ] 22. Production deployment preparation
  - Create deployment scripts and configuration
  - Set up monitoring and alerting systems
  - Prepare rollback procedures
  - Create user migration guide
  - Document new API endpoints and changes
  - _Requirements: All requirements_