# Design Document: GopiAI System Fixes

## Overview

This design addresses the critical architectural issues in GopiAI by implementing a clean separation between the backend API server (GopiAI-CrewAI) and frontend UI client (GopiAI-UI). The core fix involves replacing the broken text-parsing tool system with native OpenAI Tool Calling, implementing robust error handling, and stabilizing the UI components.

## Architecture

### High-Level System Architecture

```
┌─────────────────────┐    HTTP API    ┌─────────────────────┐
│   GopiAI-UI         │◄──────────────►│   GopiAI-CrewAI     │
│   (Frontend Client) │                │   (Backend Server)  │
├─────────────────────┤                ├─────────────────────┤
│ • Tab Management    │                │ • Tool Execution    │
│ • Chat Interface    │                │ • LLM Integration   │
│ • Error Display     │                │ • Command Safety    │
│ • User Interactions │                │ • API Endpoints     │
└─────────────────────┘                └─────────────────────┘
```

### API Communication Flow

```
User Action → UI Event → HTTP Request → Backend Processing → Tool Execution → API Response → UI Update
```

## Components and Interfaces

### Backend Components (GopiAI-CrewAI)

#### 1. Tool Definition System
**File:** `tools/gopiai_integration/tool_definitions.py`

```python
def get_tool_schema() -> List[Dict]:
    """Returns OpenAI-compatible tool schema"""
    return [
        {
            "type": "function",
            "function": {
                "name": "execute_terminal_command",
                "description": "Execute safe terminal commands",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command to execute"}
                    },
                    "required": ["command"]
                }
            }
        },
        # Additional tools: browse_website, web_search, file_operations
    ]
```

#### 2. Native Tool Calling Engine
**File:** `tools/gopiai_integration/smart_delegator.py`

```python
class SmartDelegator:
    def process_request(self, user_message: str, model_id: str) -> Dict:
        """Main request processing with native tool calling"""
        
    def _call_llm_with_tools(self, messages: List[Dict], model_id: str) -> Dict:
        """LLM call with OpenAI tool calling format"""
        
    def _execute_tool(self, function_name: str, function_args: Dict) -> str:
        """Execute tool by name with direct method calls"""
```

#### 3. Enhanced Command Executor
**File:** `tools/gopiai_integration/command_executor.py`

```python
class CommandExecutor:
    def execute_terminal_command(self, command: str) -> str:
        """Direct terminal command execution with safety checks"""
        
    def browse_website(self, url: str) -> str:
        """Web page content extraction"""
        
    def web_search(self, query: str, num_results: int = 5) -> str:
        """Internet search functionality"""
        
    def file_operations(self, operation: str, path: str, content: str = None) -> str:
        """Safe file system operations"""
```

#### 4. Error Handling System
**File:** `tools/gopiai_integration/error_handler.py`

```python
class ErrorHandler:
    @staticmethod
    def handle_llm_error(error: Exception, model_id: str) -> Dict:
        """Convert LLM errors to user-friendly API responses"""
        
    @staticmethod
    def handle_tool_error(error: Exception, tool_name: str) -> str:
        """Handle tool execution errors gracefully"""
```

### Frontend Components (GopiAI-UI)

#### 1. API Client
**File:** `gopiai/ui/api/client.py`

```python
class GopiAIAPIClient:
    def send_message(self, message: str, model_id: str = None) -> Dict:
        """Send message to backend API"""
        
    def get_available_models(self) -> List[Dict]:
        """Get list of available models"""
        
    def health_check(self) -> bool:
        """Check backend server health"""
```

#### 2. Enhanced Tab Management
**File:** `gopiai/ui/components/tab_widget.py`

```python
class TabDocumentWidget:
    def add_notebook_tab(self, title: str, content: str = "") -> QWidget:
        """Create notebook tab with proper error handling"""
        
    def _handle_tab_creation_error(self, error: Exception) -> None:
        """Handle tab creation failures gracefully"""
```

#### 3. Error Display System
**File:** `gopiai/ui/components/error_display.py`

```python
class ErrorDisplayWidget:
    def show_api_error(self, error_message: str) -> None:
        """Display API errors to user"""
        
    def show_connection_error(self) -> None:
        """Display connection issues"""
```

## Data Models

### API Request/Response Format

#### Tool Execution Request
```json
{
    "message": "List files in current directory",
    "model_id": "deepseek/deepseek-chat",
    "session_id": "session_123",
    "metadata": {
        "timestamp": "2025-07-31T10:00:00Z",
        "user_id": "user_123"
    }
}
```

#### Tool Execution Response
```json
{
    "status": "success",
    "response": "Here are the files in the current directory:\n...",
    "tools_used": [
        {
            "name": "execute_terminal_command",
            "args": {"command": "ls -la"},
            "result": "total 48\ndrwxr-xr-x 12 user user 4096 Jul 31 10:00 .\n..."
        }
    ],
    "has_commands": true,
    "model_info": {
        "model_id": "deepseek/deepseek-chat",
        "provider": "openrouter"
    },
    "execution_time": 2.34
}
```

#### Error Response
```json
{
    "status": "error",
    "message": "Rate limit exceeded for model deepseek/deepseek-chat",
    "error_code": "RATE_LIMIT_EXCEEDED",
    "retry_after": 60,
    "response": "Please try again in 60 seconds or select a different model"
}
```

### Tool Schema Format

Each tool follows OpenAI Function Calling specification:

```json
{
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": "Clear description of what the tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param_name": {
                    "type": "string|number|boolean",
                    "description": "Parameter description"
                }
            },
            "required": ["required_param"]
        }
    }
}
```

## Error Handling

### Backend Error Categories

1. **LLM Errors**
   - RateLimitError → Retry with exponential backoff
   - AuthenticationError → Return auth error message
   - InvalidRequestError → Return validation error
   - Timeout → Return timeout message

2. **Tool Execution Errors**
   - Command not allowed → Return security message
   - File not found → Return file error
   - Network error → Return connection error
   - Permission denied → Return permission error

3. **System Errors**
   - JSON parsing error → Return format error
   - Internal server error → Return generic error
   - Resource exhaustion → Return resource error

### Frontend Error Handling

1. **API Communication Errors**
   - Connection refused → Show "Backend server not available"
   - Timeout → Show "Request timed out, please try again"
   - Invalid response → Show "Invalid server response"

2. **UI Component Errors**
   - Tab creation failure → Show error message, create fallback tab
   - Widget initialization error → Use fallback widget
   - Theme loading error → Use default theme

## Testing Strategy

### Backend Testing

#### Unit Tests
- Tool schema validation
- Command safety checking
- Error handling for each error type
- API response format validation

#### Integration Tests
- End-to-end tool execution flow
- LLM integration with tool calling
- Error propagation through API layers

#### API Tests
```python
def test_tool_execution_api():
    response = client.post("/api/process", json={
        "message": "list files",
        "model_id": "test-model"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert len(response.json()["tools_used"]) > 0
```

### Frontend Testing

#### Component Tests
- Tab creation and management
- Error display components
- API client functionality

#### UI Integration Tests
- User workflow testing
- Error scenario handling
- Backend communication

#### Error Handling Tests
```python
def test_backend_connection_error():
    # Mock backend unavailable
    with patch('requests.post') as mock_post:
        mock_post.side_effect = ConnectionError()
        
        result = api_client.send_message("test")
        assert "server not available" in result["error"]
```

## Security Considerations

### Command Execution Safety
- Whitelist of allowed commands
- Path traversal prevention
- Resource usage limits
- Timeout enforcement

### API Security
- Input validation and sanitization
- Rate limiting per client
- Error message sanitization
- Logging of security events

### File System Access
- Restricted to safe directories
- File size limits
- Extension validation
- Permission checking

## Performance Considerations

### Backend Optimizations
- Connection pooling for LLM APIs
- Caching of tool schemas
- Async processing where possible
- Resource cleanup after tool execution

### Frontend Optimizations
- Lazy loading of UI components
- Efficient tab management
- Background API calls
- Error state caching

## Deployment Strategy

### Development Phase
1. Implement backend tool calling system
2. Update frontend API client
3. Test integration between components
4. Validate error handling scenarios

### Testing Phase
1. Unit test all components
2. Integration test API communication
3. End-to-end user workflow testing
4. Performance and security testing

### Production Deployment
1. Deploy backend with new tool system
2. Update frontend with API client
3. Monitor error rates and performance
4. Gradual rollout with fallback options

## Migration Plan

### Phase 1: Backend Tool System
- Remove regex-based command parsing
- Implement OpenAI tool calling
- Add comprehensive error handling
- Update API endpoints

### Phase 2: Frontend Stability
- Fix UI component crashes
- Implement proper error display
- Update API communication
- Enhance tab management

### Phase 3: Integration & Testing
- End-to-end testing
- Performance optimization
- Security validation
- Documentation updates

This design ensures clean separation between frontend and backend while providing robust tool execution and error handling capabilities.