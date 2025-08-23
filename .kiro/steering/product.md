---
inclusion: always
---

# GopiAI Product Overview

GopiAI is a modular AI desktop application with extensible architecture supporting conversational AI, semantic memory, and agent orchestration.

## Core Principles
- **Modularity**: Each GopiAI-* component is independently installable and testable
- **Memory-First**: Built-in semantic memory system for context retention across sessions
- **Agent Orchestration**: CrewAI integration for complex multi-agent workflows
- **Extensibility**: Plugin architecture supporting custom tools and integrations
- **Desktop-Native**: PySide6 GUI application, not web-based

## Architecture Patterns
- **API-First**: Internal communication via REST APIs (CrewAI server on port 5051)
- **Event-Driven**: Asynchronous communication between UI and backend services
- **Embedded Memory**: v2.0+ uses embedded txtai, no separate RAG server required

## Component Responsibilities
- **GopiAI-UI**: Desktop application, chat interface, user interactions
- **GopiAI-Core**: Shared interfaces, exceptions, schema definitions
- **GopiAI-CrewAI**: AI agent server, model management, task orchestration
- **GopiAI-Extensions**: Plugin system, external integrations, browser tools
- **GopiAI-Widgets**: Reusable UI components, themes, layouts
- **GopiAI-App**: Application packaging, distribution, MCP server setup

## Development Guidelines
- **Error Handling**: Always implement graceful degradation when AI services unavailable
- **Logging**: Extensive debug logging to component-specific .log files
- **Configuration**: Use .env files for secrets, steering files for behavior rules
- **Testing**: pytest for unit tests, pytest-qt for GUI components
- **Memory Management**: Implement proper cleanup for long-running chat sessions

## Integration Points
- **CrewAI API**: RESTful communication for agent tasks and model queries
- **Memory System**: txtai-based semantic search and context retrieval
- **External Tools**: MCP protocol for browser automation, file operations
- **UI Events**: Qt signals/slots for responsive user interface updates