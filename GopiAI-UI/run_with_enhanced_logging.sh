#!/bin/bash

# Enable debug mode
set -x

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR" || exit 1

# Set environment variables for Qt debugging
export QT_DEBUG_PLUGINS=1
export QT_LOGGING_RULES="*.debug=true;qt.*.debug=false"

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Run the application with Python's debug output
PYTHONPATH="$SCRIPT_DIR" \
python -v -X dev "$SCRIPT_DIR/main_with_logging.py" "$@" 2>&1 | tee "$SCRIPT_DIR/logs/startup_$(date +%Y%m%d_%H%M%S).log"

# Print the location of the main log file
echo -e "\nApplication logs can be found in:\n$SCRIPT_DIR/logs/gopiai_ui.log"
