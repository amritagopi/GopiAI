# GopiAI Project Overview

This document provides a comprehensive overview of the GopiAI project, its architecture, and development conventions, intended to be used as instructional context for future interactions.

## Project Overview

GopiAI is a comprehensive artificial intelligence platform with a modular architecture. It integrates agent orchestration using CrewAI, a modern user interface built with PySide6, and advanced capabilities for working with language models. The project is written in Python and utilizes a variety of libraries for AI/ML, web APIs, and testing.

### Key Features:

*   **Agent Coordination:** Integration with CrewAI for orchestrating AI agents.
*   **Smart LLM Switching:** Automatic switching of language model providers based on request limits.
*   **Modern UI:** A Qt-based application with an adaptive design.
*   **Advanced RAG Memory:** Context-aware responses with retrieval-augmented generation.
*   **Comprehensive Testing:** Automated tests and system validation.
*   **Real-time Monitoring:** Tracking of application status and performance metrics.

## Architecture

The project is divided into several key modules:

*   **GopiAI-UI:** The main user interface, built with PySide6. It is the entry point of the application.
*   **GopiAI-CrewAI:** The backend component that integrates with CrewAI for agent-based tasks. It runs as a separate server.
*   **GopiAI-Assets:** Contains assets for the application, such as images and styles.
*   **rag_memory_system:** The retrieval-augmented generation memory system.
*   **test_infrastructure:** Contains the testing framework and related utilities.

The UI and the CrewAI server communicate via a REST API, which allows for loose coupling and independent development of the components.

## Building and Running

### Setup

To set up the development environment, run the following script:

```bash
chmod +x setup_linux.sh
./setup_linux.sh
```

This script will create a Python virtual environment, install all the necessary dependencies from `requirements.txt`, and set the required permissions for the scripts.

### Running the Application

To start the GopiAI application, run the following command:

```bash
source start_linux.sh
```

This script activates the virtual environment and launches the main UI. The UI, in turn, automatically starts the CrewAI server. The web interface will be available at `http://localhost:8000`.

### Running Tests

To run the test suite, use the following command:

```bash
./scripts/run_tests.py
```

You can also run specific categories of tests:

```bash
./scripts/run_tests.py --category unit
```

## Development Conventions

*   **Coding Style:** The project follows the standard Python coding conventions (PEP 8).
*   **Virtual Environments:** The project uses a dedicated virtual environment (`.venv`) to manage dependencies.
*   **Testing:** The project has a comprehensive test suite, including unit, integration, and end-to-end tests. All new code should be accompanied by corresponding tests.
*   **Modularity:** The project is designed to be modular, with different components separated into their own directories. This allows for independent development and maintenance.
