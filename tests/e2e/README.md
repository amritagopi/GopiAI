# End-to-End Tests for GopiAI System

This directory contains comprehensive end-to-end (E2E) tests that validate the complete GopiAI system functionality from user interaction through backend processing to AI response and memory persistence.

## Overview

The E2E tests cover four main areas as specified in the requirements:

1. **Complete Conversation Flow** - Full cycle AI conversations with response generation
2. **Memory Persistence** - Context preservation across sessions and service restarts
3. **Service Recovery** - System resilience after service failures
4. **Multiple Users** - Concurrent user support and session isolation

## Test Structure

```
tests/e2e/
├── test_complete_scenarios.py    # Main E2E test implementations
├── test_runner_e2e.py           # Specialized E2E test runner
├── README.md                    # This documentation
└── conftest.py                  # E2E-specific pytest configuration
```

## Test Classes

### TestCompleteConversationFlow
Tests complete conversation cycles including:
- Full conversation flow from user input to AI response
- Model switching during conversations
- Error recovery and graceful degradation
- Response quality and context preservation

### TestMemoryPersistence
Tests memory system functionality:
- Context persistence across different sessions
- Conversation history storage and retrieval
- Memory system recovery after service restarts
- Search functionality for past conversations

### TestServiceRecovery
Tests system resilience:
- CrewAI server failure and recovery
- Memory system failure and recovery
- Concurrent service failures
- Data integrity during failures

### TestMultipleUsers
Tests multi-user scenarios:
- Concurrent conversations from multiple users
- User session isolation and privacy
- Load handling under multiple user requests
- Performance metrics under load

## Running E2E Tests

### Prerequisites

1. **Service Dependencies**: Ensure all required services can be started:
   - CrewAI server (GopiAI-CrewAI)
   - Memory system (txtai)
   

2. **Environment Setup**: The tests will automatically set up test isolation, but ensure:
   - All virtual environments are properly configured
   - Required Python packages are installed in each environment
   - API keys are available (can be mock keys for testing)

### Using the E2E Test Runner

The specialized E2E test runner (`test_runner_e2e.py`) provides the easiest way to run these tests:

```bash
# Validate E2E environment setup
python tests/e2e/test_runner_e2e.py --validate-only

# Run all E2E tests
python tests/e2e/test_runner_e2e.py

# Run specific test categories
python tests/e2e/test_runner_e2e.py --conversation-flow
python tests/e2e/test_runner_e2e.py --memory-persistence
python tests/e2e/test_runner_e2e.py --service-recovery
python tests/e2e/test_runner_e2e.py --multiple-users

# Run specific test class
python tests/e2e/test_runner_e2e.py --test-class TestCompleteConversationFlow
```

### Using pytest directly

```bash
# Run all E2E tests
pytest tests/e2e/ -m e2e -v

# Run specific test file
pytest tests/e2e/test_complete_scenarios.py -v

# Run specific test class
pytest tests/e2e/test_complete_scenarios.py::TestCompleteConversationFlow -v

# Run specific test method
pytest tests/e2e/test_complete_scenarios.py::TestCompleteConversationFlow::test_full_conversation_cycle -v
```

### Integration with Master Test Runner

The E2E tests are integrated with the master test runner:

```bash
# Run E2E tests as part of comprehensive test suite
python test_infrastructure/master_test_runner.py --include-e2e

# Run only E2E tests through master runner
python test_infrastructure/master_test_runner.py --test-type e2e
```

## Test Environment Management

### Automatic Service Management

The E2E tests automatically:
- Start required services (CrewAI server, memory system)
- Set up test data isolation
- Wait for services to become healthy
- Clean up after test completion

### Test Isolation

Each E2E test run uses isolated:
- Test data directories
- Separate conversation storage
- Isolated memory indices
- Mock AI service responses

### Service Health Monitoring

The tests continuously monitor service health and will:
- Wait for services to start properly
- Validate service readiness before running tests
- Report service issues if tests fail
- Provide detailed health reports

## Mock Services and Data

### AI Service Mocking

The tests use sophisticated AI service mocks that:
- Provide realistic responses for different providers (OpenAI, Anthropic, Google)
- Support conversation context and follow-up responses
- Simulate different response times and error conditions
- Track usage statistics and rate limiting

### Test Data Generation

Tests automatically generate:
- Realistic conversation scenarios
- Multiple user sessions with different contexts
- Various message types and conversation flows
- Error conditions and recovery scenarios

## Performance and Load Testing

### Concurrent User Testing

The multiple users tests validate:
- System performance under concurrent load
- Response time consistency across users
- Memory usage and resource management
- Session isolation under load

### Performance Metrics

Tests measure and validate:
- Response times (should be < 30 seconds per request)
- Average response time (should be < 15 seconds)
- Service startup time (should be < 60 seconds)
- Memory system search performance

## Troubleshooting

### Common Issues

1. **Services fail to start**
   - Check that virtual environments are properly configured
   - Verify required Python packages are installed
   - Check port availability (5051 for CrewAI, 8000 for memory)

2. **Tests timeout**
   - Increase timeout values in test configuration
   - Check system resources (CPU, memory)
   - Verify network connectivity for API calls

3. **Memory system issues**
   - Ensure txtai environment is properly set up
   - Check disk space for memory indices
   - Verify write permissions in test directories

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
# Set debug environment variable
export GOPIAI_DEBUG=1

# Run tests with verbose output
python tests/e2e/test_runner_e2e.py --verbose
```

### Service Logs

Check service logs for detailed error information:
- CrewAI server: `GopiAI-CrewAI/test_crewai_server.log`
- Memory system: `rag_memory_system/test_memory_system.log`
- UI application: `GopiAI-UI/test_ui_app.log`

## Test Configuration

### Environment Variables

Key environment variables for E2E tests:

- `GOPIAI_TEST_MODE=true` - Additional test mode flag
- `CREWAI_TEST_MODE=true` - CrewAI test mode
- `TXTAI_TEST_MODE=true` - Memory system test mode

### Timeouts and Limits

Default timeouts (can be overridden):
- Service startup: 60 seconds
- Service health check: 30 seconds
- API request timeout: 30 seconds
- Test execution timeout: 300 seconds per test

### Test Data Paths

Test data is stored in temporary directories:
- Conversations: `test_conversations/`
- Memory indices: `test_memory/`
- Logs: `test_logs/`
- Cache: `test_cache/`
- Configuration: `test_config/`

## Contributing

When adding new E2E tests:

1. Follow the existing test class structure
2. Use the provided fixtures and mocks
3. Ensure proper cleanup in test teardown
4. Add appropriate test markers (`@pytest.mark.e2e`, `@pytest.mark.slow`)
5. Document any new test scenarios in this README
6. Update the test runner if adding new test categories

## Requirements Mapping

These E2E tests fulfill the following requirements from the specification:

- **Requirement 4.1**: Full user scenarios from start to finish
- **Requirement 4.2**: Context preservation between sessions
- **Requirement 4.3**: Recovery testing after service failures
- **Additional**: Multiple user support and load testing

The tests provide comprehensive validation that the GopiAI system works correctly as an integrated whole, not just as individual components.