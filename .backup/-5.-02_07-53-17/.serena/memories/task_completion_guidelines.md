# Task Completion Guidelines

When completing tasks in the GopiAI project, follow these guidelines:

## Code Changes
1. **Understand the Context**: Before making changes, understand the surrounding code and its purpose
2. **Follow Existing Patterns**: Match the coding style and patterns used in the file
3. **Preserve Functionality**: Ensure your changes don't break existing functionality
4. **Test Your Changes**: Manually test the changes to verify they work as expected
5. **Update Related Components**: If you change one part of the code, update any related parts

## UI Changes
1. **Maintain Consistency**: Follow the existing UI design patterns
2. **Support Localization**: Use the translation system (`self._translate()`) for all user-visible text
3. **Support Both Themes**: Ensure your UI changes work with both light and dark themes
4. **Use Existing Components**: Reuse existing UI components when possible
5. **Follow Qt/PySide6 Patterns**: Use standard Qt patterns for signals, slots, and layouts

## Agent and Tool Changes
1. **Update Documentation**: Document any new tools or agent capabilities
2. **Handle Errors Gracefully**: Include proper error handling
3. **Test with Different Models**: Ensure changes work with all supported LLM models
4. **Consider Performance**: Be mindful of token usage and processing time

## Internationalization
1. **Update Translation Files**: Add new keys to all language files (en.json, ru.json)
2. **Use Translation Keys**: All user-visible text should use the translation system
3. **Test With All Languages**: Verify your changes work correctly in all supported languages

## File Management
1. **Organize New Files**: Place new files in the appropriate directories
2. **Update Imports**: Update import statements when moving or renaming files
3. **Clean Up Temporary Files**: Remove any temporary files created during development

## After Task Completion
1. **Review Your Changes**: Check for any bugs, typos, or performance issues
2. **Test End-to-End**: Test the entire feature flow, not just your changes
3. **Update Documentation**: If needed, update any relevant documentation
4. **Check for Warnings/Errors**: Ensure your code doesn't generate warnings or errors
5. **Clean Up**: Remove any debugging code or commented-out code that's no longer needed