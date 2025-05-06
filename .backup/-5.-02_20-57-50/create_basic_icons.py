#!/usr/bin/env python
"""
Script for creating basic icons for the GopiAI application.
Runs when the application starts if the necessary icons are missing.
"""
import base64
import json
import os
import shutil

# SVG icon for tab closing
CLOSE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8 1.33A6.67 6.67 0 1 1 1.33 8 6.67 6.67 0 0 1 8 1.33zM8 0a8 8 0 1 0 8 8 8 8 0 0 0-8-8zm3.7 11.36a.62.62 0 0 1-.01.88.63.63 0 0 1-.88 0L8 9.44l-2.81 2.8a.63.63 0 0 1-.88-.01.62.62 0 0 1 0-.88L7.11 8.5 4.3 5.7a.63.63 0 0 1 .01-.89.62.62 0 0 1 .88 0L8 7.61l2.81-2.8a.63.63 0 0 1 .88.01.62.62 0 0 1 0 .88L8.88 8.5z"/>
</svg>"""

# Manifest with basic icons
BASIC_MANIFEST = {
    "icons": {
        "app_icon": "app_icon.png",
        "close": "close.svg",
        "open": "open.svg",
        "save": "save.svg",
        "new_document": "new_document.svg",
        "settings": "settings.svg",
        "folder": "folder.svg",
        "python": "python.svg",
        "text": "text.svg",
        "html": "html.svg",
        "javascript": "javascript.svg",
        "css": "css.svg",
        "json": "json.svg",
        "image_png": "image_png.svg",
        "terminal": "terminal.svg",
        "browser": "browser.svg",
        "run": "run.svg",
        "home": "home.svg",
        "info": "info.svg",
        "documentation": "documentation.svg",
        "preferences": "preferences.svg",
        "emoji": "emoji.svg",
        "link": "link.svg",
        "shell": "shell.svg"
    }
}

# Basic SVG icons for main functions
BASIC_ICONS = {
    "close.svg": CLOSE_SVG,
    "open.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        <path fill="currentColor" d="M14.36 4.74h-4.8V3.51a1.33 1.33 0 0 0-1.33-1.33H3.97a1.33 1.33 0 0 0-1.33 1.33v8.9h11.72a1.33 1.33 0 0 0 1.33-1.33V6.08a1.33 1.33 0 0 0-1.33-1.34z"/>
    </svg>""",
    "save.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        <path fill="currentColor" d="M13.5 3h-1.88V5.5h-7V3H2.5a.5.5 0 0 0-.5.5v9a.5.5 0 0 0 .5.5h11a.5.5 0 0 0 .5-.5v-9a.5.5 0 0 0-.5-.5zM8 11a1.5 1.5 0 1 1 1.5-1.5A1.5 1.5 0 0 1 8 11zM10.82 3h-5.7v1.8h5.7z"/>
    </svg>""",
    "new_document.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        <path fill="currentColor" d="M9.5 1.5H4a1 1 0 0 0-1 1v11a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V5zm.1 3h-2.6V1.9l2.6 2.6z"/>
    </svg>""",
    "folder.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        <path fill="currentColor" d="M7 2H2a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1H8z"/>
    </svg>""",
    "python.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        <path fill="#3572A5" d="M7.8 1.5c-4 0-3.7 1.7-3.7 1.7l.1 1.8h3.8v.5H2.8S1 5.5 1 9.2c0 3.7 1.6 3.5 1.6 3.5h1v-1.7s0-2 2-2h3.4s1.9 0 1.9-1.8V4.3s.3-2.8-3-2.8zm-2.1 1.6c.4 0 .7.3.7.7 0 .4-.3.7-.7.7-.4 0-.7-.3-.7-.7 0-.4.3-.7.7-.7z"/>
        <path fill="#FFD43B" d="M8.2 14.5c4 0 3.7-1.7 3.7-1.7l-.1-1.8H8.1v-.5h5.2s1.8 0 1.8-3.8c0-3.7-1.6-3.5-1.6-3.5h-1v1.7s0 2-2 2H7.1s-1.9 0-1.9 1.8v2.9s-.3 2.8 3 2.8zm2.1-1.6c-.4 0-.7-.3-.7-.7 0-.4.3-.7.7-.7.4 0 .7.3.7.7 0 .4-.3.7-.7.7z"/>
    </svg>""",
    "settings.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        <path fill="currentColor" d="M13.3 5.2l-.8-.8c-.6-.6-1.5-.6-2.1 0l-5.5 5.5c-.6.6-.6 1.5 0 2.1l.8.8c.6.6 1.5.6 2.1 0l5.5-5.5c.6-.6.6-1.5 0-2.1z"/>
        <circle cx="5" cy="5" r="1.5" fill="currentColor"/>
        <circle cx="11" cy="11" r="1.5" fill="currentColor"/>
    </svg>""",
    "terminal.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        <path fill="currentColor" d="M1.5 2A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13zm5.41 7.59L4.5 12l1.41 1.41 4.5-4.5-4.5-4.5L4.5 5.82 7.09 8.5z"/>
    </svg>"""
}

def create_basic_icons():
    """Creates basic icons in the assets/icons directory if they are missing."""
    # Path to icons directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(script_dir, "assets", "icons")

    # Create assets/icons directory if it doesn't exist
    os.makedirs(icons_dir, exist_ok=True)

    # Check if manifest exists and create it if not
    manifest_path = os.path.join(icons_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(BASIC_MANIFEST, f, indent=2)
        print(f"Created icons manifest at {manifest_path}")

    # Create basic icons
    for icon_name, svg_content in BASIC_ICONS.items():
        icon_path = os.path.join(icons_dir, icon_name)
        if not os.path.exists(icon_path):
            with open(icon_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            print(f"Created icon: {icon_name}")

    # Check for app icon
    app_icon_path = os.path.join(icons_dir, "app_icon.png")
    if not os.path.exists(app_icon_path):
        # Create a simple app icon (50x50 pixels) if it's missing
        try:
            # Try to copy from elsewhere if possible
            default_app_icon = os.path.join(script_dir, "picked_icons", "for_gopiai", "app_icon.png")
            if os.path.exists(default_app_icon):
                shutil.copy(default_app_icon, app_icon_path)
                print(f"Copied app icon from {default_app_icon}")
            else:
                # Do nothing, application will use system icon
                print("App icon not found, using system default")
        except Exception as e:
            print(f"Error creating app icon: {e}")

    print("Basic icons creation completed")
    return True

# If script is run directly, create icons
if __name__ == "__main__":
    create_basic_icons()
