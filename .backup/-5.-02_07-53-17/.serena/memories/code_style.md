# Code Style and Conventions

## General Style
- **Python PEP 8**: The code generally follows PEP 8 style guidelines
- **Docstrings**: Classes and functions include docstrings explaining their purpose
- **Type Hints**: Some functions include type hints for parameters and return values
- **Comments**: Code includes explanatory comments for complex logic

## Naming Conventions
- **Classes**: CamelCase (e.g., `ChatWidget`, `MainWindow`, `CodeEditor`)
- **Functions/Methods**: snake_case with leading underscore for private methods (e.g., `_setup_ui`, `_connect_signals`)
- **Variables**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **UI Elements**: Descriptive names indicating the element type (e.g., `chat_widget`, `project_tree`, `save_action`)

## File Organization
- **UI Code**: Located in `app/ui/` directory
- **Agent Code**: Located in `app/agent/` directory
- **Tools**: Located in `app/tool/` directory
- **Flow Logic**: Located in `app/flow/` directory
- **Assets**: Located in `assets/` directory (including icons and fonts)

## UI Development
- **Qt Designer**: May be used for some UI layouts
- **QSS**: Used for styling via separate theme files in `app/ui/themes/`
- **Signal/Slot Pattern**: Used for communication between UI components

## Error Handling
- Try/except blocks are used for operations that might fail
- Error messages are logged and sometimes displayed to the user

## Internationalization
- The application supports English and Russian
- Translation files are stored in JSON format in `app/ui/i18n/`
- Translation is handled through a custom `JsonTranslationManager`

## Testing
- Test files are located in the `tests/` directory
- Pytest is used as the testing framework