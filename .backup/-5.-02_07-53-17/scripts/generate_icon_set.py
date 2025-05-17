#!/usr/bin/env python
"""
Script for generating a uniform set of SVG icons for GopiAI.

The script creates a complete set of icons in a unified style based on
basic SVG templates. The icons will be placed in the assets/icons directory,
then the compile_icons.py script will be used to compile
the resources into icons_rc.py.
"""

import os
import sys
import json
import argparse
import shutil
import subprocess
from pathlib import Path


# Main colors for icons
ICON_COLORS = {
    "primary": "#4285F4",        # Google blue
    "secondary": "#34A853",      # Google green
    "warning": "#FBBC05",        # Google yellow
    "danger": "#EA4335",         # Google red
    "dark": "#202124",           # Google dark gray
    "light": "#FFFFFF",          # White
    "gray": "#9AA0A6",           # Google gray
    "code": "#673AB7",           # Purple for code
    "text": "#5F6368",           # Google text color
    "folder": "#FFA000",         # Folder color
    "python": "#3572A5",         # Python color
    "javascript": "#F7DF1E",     # JavaScript color
    "html": "#E34F26",           # HTML color
    "css": "#1572B6",            # CSS color
}

# SVG templates for basic icons
ICON_TEMPLATES = {
    "file": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="{color}" d="M10 1H3c-.6 0-1 .4-1 1v12c0 .6.4 1 1 1h10c.6 0 1-.4 1-1V4l-4-3zm1 3h-3V1l3 3z"/>
</svg>""",

    "folder": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="{color}" d="M14 4H8L6 2H2C.9 2 0 2.9 0 4v8c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2z"/>
</svg>""",

    "code": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="{color}" d="M5.5 11.5L2 8l3.5-3.5L4 3 0 8l4 5 1.5-1.5zm5 0L14 8l-3.5-3.5L12 3l4 5-4 5-1.5-1.5z"/>
</svg>""",

    "terminal": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="{color}" d="M1.5 2A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13zm5.41 7.59L4.5 12l1.41 1.41 4.5-4.5-4.5-4.5L4.5 5.82 7.09 8.5z"/>
</svg>""",

    "settings": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="{color}" d="M15.2 6.7l-1.4-.3c-.1-.4-.3-.8-.5-1.2l.7-1.2c.2-.4.2-.9-.2-1.2l-1.2-1.2c-.3-.3-.8-.4-1.2-.2l-1.2.7c-.4-.2-.8-.3-1.2-.5L8.8.5C8.7.2 8.4 0 8 0s-.7.2-.8.5l-.3 1.4c-.4.1-.8.3-1.2.5l-1.2-.7c-.4-.2-.9-.1-1.2.2L2.1 3.1c-.3.3-.4.8-.2 1.2l.7 1.2c-.2.4-.3.8-.5 1.2l-1.4.3c-.3.1-.5.4-.5.8v1.7c0 .4.2.7.5.8l1.4.3c.1.4.3.8.5 1.2l-.7 1.2c-.2.4-.1.9.2 1.2l1.2 1.2c.3.3.8.4 1.2.2l1.2-.7c.4.2.8.4 1.2.5l.3 1.4c.1.3.4.5.8.5h1.7c.4 0 .7-.2.8-.5l.3-1.4c.4-.1.8-.3 1.2-.5l1.2.7c.4.2.9.1 1.2-.2l1.2-1.2c.3-.3.4-.8.2-1.2l-.7-1.2c.2-.4.4-.8.5-1.2l1.4-.3c.3-.1.5-.4.5-.8V7.5c0-.4-.2-.7-.5-.8zM8 11c-1.7 0-3-1.3-3-3s1.3-3 3-3 3 1.3 3 3-1.3 3-3 3z"/>
</svg>""",

    "browser": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="{color}" d="M15 1H1c-.6 0-1 .4-1 1v12c0 .6.4 1 1 1h14c.6 0 1-.4 1-1V2c0-.6-.4-1-1-1zm-1 12H2V5h12v8zm0-9H2V2h12v2z"/>
</svg>""",

    "arrow": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="{color}" d="M8 0L6.59 1.41 12.17 7H0v2h12.17l-5.58 5.59L8 16l8-8z"/>
</svg>""",

    "save": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="{color}" d="M13.5 3h-11C1.7 3 1 3.7 1 4.5v7c0 .8.7 1.5 1.5 1.5h11c.8 0 1.5-.7 1.5-1.5v-7c0-.8-.7-1.5-1.5-1.5zM8 11c-1.7 0-3-1.3-3-3s1.3-3 3-3 3 1.3 3 3-1.3 3-3 3zm3-7H2V3h9v1z"/>
</svg>""",

    "open": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="{color}" d="M14 5H8L6 3H2C.9 3 0 3.9 0 5v6c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2z"/>
</svg>""",

    "close": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="{color}" d="M12.7 4.7l-1.4-1.4L8 6.6 4.7 3.3 3.3 4.7 6.6 8l-3.3 3.3 1.4 1.4L8 9.4l3.3 3.3 1.4-1.4L9.4 8z"/>
</svg>""",

    "home": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="{color}" d="M8 1.4l-8 7.2h2v6h4v-4h4v4h4v-6h2z"/>
</svg>""",
}


def generate_icon_set(icons_dir, force=False):
    """
    Generates a set of SVG icons in the specified directory.

    Args:
        icons_dir: Path to the directory to save icons to (assets/icons)
        force: If True, overwrites existing icons

    Returns:
        Number of created icons
    """
    # Create directory if it doesn't exist
    os.makedirs(icons_dir, exist_ok=True)

    # Icons manifest
    manifest = {
        "icons": {}
    }

    # Created icons counter
    created_count = 0

    # Create basic icons
    for name, template in ICON_TEMPLATES.items():
        icon_path = os.path.join(icons_dir, f"{name}.svg")
        if not os.path.exists(icon_path) or force:
            # Choose main color for the icon
            color = ICON_COLORS.get(name, ICON_COLORS["primary"])

            # Fill template with color
            icon_content = template.format(color=color)

            # Save icon
            with open(icon_path, "w", encoding="utf-8") as f:
                f.write(icon_content)

            created_count += 1
            manifest["icons"][name] = f"{name}.svg"
            print(f"Created icon: {name}.svg")

    # Create file icons for different programming languages
    file_types = {
        "python": {"ext": "py", "color": ICON_COLORS["python"]},
        "javascript": {"ext": "js", "color": ICON_COLORS["javascript"]},
        "html": {"ext": "html", "color": ICON_COLORS["html"]},
        "css": {"ext": "css", "color": ICON_COLORS["css"]},
        "text": {"ext": "txt", "color": ICON_COLORS["text"]},
        "markdown": {"ext": "md", "color": ICON_COLORS["text"]},
        "json": {"ext": "json", "color": ICON_COLORS["text"]},
        "batch": {"ext": "bat", "color": ICON_COLORS["text"]},
        "shell": {"ext": "sh", "color": ICON_COLORS["text"]},
        "typescript": {"ext": "ts", "color": ICON_COLORS["primary"]},
    }

    for name, file_info in file_types.items():
        icon_path = os.path.join(icons_dir, f"{file_info['ext']}.svg")
        if not os.path.exists(icon_path) or force:
            # Use file template with color for this type
            icon_content = ICON_TEMPLATES["file"].format(color=file_info["color"])

            # Save icon
            with open(icon_path, "w", encoding="utf-8") as f:
                f.write(icon_content)

            created_count += 1
            manifest["icons"][file_info['ext']] = f"{file_info['ext']}.svg"
            print(f"Created icon: {file_info['ext']}.svg")

    # Create control icons
    controls = {
        "back": {"template": "arrow", "color": ICON_COLORS["gray"], "transform": "rotate(180 8 8)"},
        "forward": {"template": "arrow", "color": ICON_COLORS["gray"]},
        "refresh": {"template": "arrow", "color": ICON_COLORS["gray"], "transform": "rotate(315 8 8)"},
        "new_document": {"template": "file", "color": ICON_COLORS["primary"]},
        "new_chat": {"template": "terminal", "color": ICON_COLORS["secondary"]},
    }

    for name, control_info in controls.items():
        icon_path = os.path.join(icons_dir, f"{name}.svg")
        if not os.path.exists(icon_path) or force:
            # Use template with needed color
            template = ICON_TEMPLATES[control_info["template"]]

            # Add transformation if specified
            if "transform" in control_info:
                template = template.replace("<path ", f"<path transform=\"{control_info['transform']}\" ")

            icon_content = template.format(color=control_info["color"])

            # Save icon
            with open(icon_path, "w", encoding="utf-8") as f:
                f.write(icon_content)

            created_count += 1
            manifest["icons"][name] = f"{name}.svg"
            print(f"Created icon: {name}.svg")

    # Save manifest
    manifest_path = os.path.join(icons_dir, "manifest.json")
    existing_manifest = {}

    # Load existing manifest if it exists
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                existing_manifest = json.load(f)
        except Exception as e:
            print(f"Error reading existing manifest: {e}")

    # Merge manifests
    if "icons" in existing_manifest:
        for name, path in manifest["icons"].items():
            existing_manifest["icons"][name] = path
    else:
        existing_manifest = manifest

    # Save updated manifest
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(existing_manifest, f, indent=2)

    print(f"Icons manifest updated: {manifest_path}")
    print(f"Created {created_count} icons")

    return created_count


def compile_icons():
    """
    Compiles icons using the compile_icons.py script.

    Returns:
        True if compilation is successful, False otherwise
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    compile_script = os.path.join(project_root, "compile_icons.py")

    if not os.path.exists(compile_script):
        print(f"Error: Icon compilation script not found: {compile_script}")
        return False

    try:
        result = subprocess.run([sys.executable, compile_script],
                              check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Compilation warnings: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error compiling icons: {e}")
        print(f"Output: {e.stdout}")
        print(f"Errors: {e.stderr}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Generates a uniform set of SVG icons for GopiAI.')
    parser.add_argument('--force', action='store_true', help='Overwrite existing icons')
    parser.add_argument('--no-compile', action='store_true', help='Do not compile icons after generation')

    args = parser.parse_args()

    # Determine path to icons directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    icons_dir = os.path.join(project_root, "assets", "icons")

    # Generate icon set
    created_count = generate_icon_set(icons_dir, args.force)

    # Compile icons if --no-compile is not specified
    if not args.no_compile and created_count > 0:
        print("\nCompiling icons...")
        if compile_icons():
            print("Icon compilation completed successfully")
        else:
            print("Error compiling icons")


if __name__ == "__main__":
    main()
