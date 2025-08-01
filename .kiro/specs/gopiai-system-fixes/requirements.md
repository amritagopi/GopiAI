# Requirements Document: GopiAI System Fixes

## Introduction

This specification addresses critical system failures in the GopiAI application that prevent normal operation. The system currently suffers from broken tool parsing, UI crashes, and poor error handling that make the application unusable. This spec focuses on fixing the core architecture while maintaining proper separation between backend API server and frontend UI client.

## Requirements

### Requirement 1: Fix Backend Tool Execution System

**User Story:** As a user, I want my commands and tool requests to be executed properly so that I can interact with the system effectively.

#### Acceptance Criteria

1. WHEN a user sends a message requesting tool usage THEN the backend SHALL use native OpenAI Tool Calling instead of text parsing
2. WHEN the LLM returns tool_calls THEN the system SHALL execute the requested tools directly without regex parsing
3. WHEN a tool execution completes THEN the system SHALL return the result in a structured API response
4. WHEN the backend processes tool requests THEN it SHALL NOT use any regex patterns like `lss*([^n]*)`
5. WHEN tools are defined THEN they SHALL use standard OpenAI function calling schema format

### Requirement 2: Implement Robust Error Handling

**User Story:** As a user, I want to receive clear error messages when something goes wrong so that I understand what happened and can take appropriate action.

#### Acceptance Criteria

1. WHEN an API rate limit is exceeded THEN the system SHALL return a clear error message and retry automatically
2. WHEN an LLM returns an empty response THEN the system SHALL provide a meaningful error message instead of crashing
3. WHEN a tool execution fails THEN the system SHALL return the error details in the API response
4. WHEN authentication fails THEN the system SHALL return a specific authentication error message
5. WHEN any backend error occurs THEN it SHALL be logged with full details for debugging

### Requirement 3: Fix UI Stability Issues

**User Story:** As a user, I want the interface to remain stable when creating new documents or tabs so that I can work without crashes.

#### Acceptance Criteria

1. WHEN a user creates a new notebook tab THEN the UI SHALL NOT crash due to widget lifecycle issues
2. WHEN a user opens the terminal THEN it SHALL appear in a tab within the main window, not as a floating window
3. WHEN a user right-clicks on tabs THEN the context menu SHALL work correctly for all close operations
4. WHEN all tabs are closed THEN the background image SHALL be displayed properly
5. WHEN the UI encounters an error THEN it SHALL display an error message instead of crashing

### Requirement 4: Ensure Proper API Communication

**User Story:** As a developer, I want clean separation between frontend and backend so that the system is maintainable and scalable.

#### Acceptance Criteria

1. WHEN the UI needs to execute tools THEN it SHALL send requests only through the HTTP API endpoints
2. WHEN the backend processes requests THEN it SHALL return responses in consistent JSON format
3. WHEN errors occur THEN they SHALL be communicated through API response status and error fields
4. WHEN the UI displays tool results THEN it SHALL receive them only through API responses
5. WHEN the system starts THEN the UI SHALL NOT import any backend modules directly

### Requirement 5: Implement Safe Command Execution

**User Story:** As a user, I want to execute terminal commands safely so that I can work with the system without security risks.

#### Acceptance Criteria

1. WHEN a terminal command is requested THEN the system SHALL validate it against a whitelist of safe commands
2. WHEN dangerous commands are attempted THEN the system SHALL reject them with a clear explanation
3. WHEN commands are executed THEN they SHALL have appropriate timeouts to prevent hanging
4. WHEN command execution fails THEN the system SHALL return both stdout and stderr information
5. WHEN working directories are specified THEN the system SHALL validate and use them safely

### Requirement 6: Provide Comprehensive Tool Support

**User Story:** As a user, I want access to various tools (terminal, web browsing, file operations) so that I can accomplish diverse tasks.

#### Acceptance Criteria

1. WHEN I request terminal operations THEN the system SHALL execute safe shell commands
2. WHEN I request web browsing THEN the system SHALL fetch and return web page content
3. WHEN I request web search THEN the system SHALL return relevant search results
4. WHEN I request file operations THEN the system SHALL safely read, write, and list files
5. WHEN any tool is used THEN the results SHALL be returned through the API in a consistent format

### Requirement 7: Maintain System Performance

**User Story:** As a user, I want the system to respond quickly and handle multiple requests efficiently so that my workflow is not interrupted.

#### Acceptance Criteria

1. WHEN multiple tool calls are made THEN the system SHALL limit iterations to prevent infinite loops
2. WHEN rate limits are hit THEN the system SHALL implement exponential backoff retry logic
3. WHEN large outputs are generated THEN they SHALL be truncated appropriately for display
4. WHEN the system is under load THEN it SHALL maintain responsive API endpoints
5. WHEN resources are used THEN they SHALL be properly cleaned up to prevent memory leaks

## Success Criteria

The system will be considered successfully fixed when:

1. ✅ Users can execute terminal commands without "command not allowed" errors
2. ✅ The UI remains stable during normal operations (creating tabs, opening terminals)
3. ✅ Error messages are clear and actionable rather than empty responses
4. ✅ All tool operations work through proper API communication
5. ✅ The system handles rate limits and other API errors gracefully
6. ✅ Backend and frontend remain properly separated with no direct imports

## Technical Constraints

- Backend must use OpenAI-compatible tool calling format
- Frontend must communicate only through HTTP API
- All tool executions must be validated for security
- Error handling must be comprehensive at both API and UI levels
- System must support multiple LLM providers through consistent interface