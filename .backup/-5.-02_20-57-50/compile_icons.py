import os
import sys
import platform
import subprocess
from pathlib import Path

def print_separator():
    print("="*50)

def compile_resources():
    """Compile .qrc file into Python module."""
    print("Compiling icon resources")

    # Path to icons resource file
    icons_qrc = os.path.join(os.getcwd(), "icons.qrc")

    # Generate .qrc file based on icons directory content
    if generate_qrc_file():
        print(f"File {icons_qrc} generated")
    else:
        print(f"Error generating {icons_qrc}")
        return False

    # Define command for resource compilation
    if platform.system() == "Windows":
        pyside_rcc = os.path.join(sys.prefix, "Scripts", "pyside6-rcc.exe")
    else:
        pyside_rcc = os.path.join(sys.prefix, "bin", "pyside6-rcc")

    # Check for pyside6-rcc
    if not os.path.exists(pyside_rcc):
        print(f"Error: pyside6-rcc not found at {pyside_rcc}")
        print("Trying to use from PATH...")
        if platform.system() == "Windows":
            pyside_rcc = "pyside6-rcc.exe"
        else:
            pyside_rcc = "pyside6-rcc"

    # Output Python module file
    output_file = os.path.join(os.getcwd(), "icons_rc.py")

    # Form and execute command
    cmd = [pyside_rcc, "-o", output_file, icons_qrc]
    print(f"Executing command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Resource compilation completed successfully")
        print(f"File created: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error compiling resources: {e}")
        print(f"Output: {e.stdout}")
        print(f"Errors: {e.stderr}")
        return False

def generate_qrc_file():
    """Generate .qrc file based on icons directory content."""
    icons_dir = os.path.join(os.getcwd(), "assets", "icons")
    qrc_file = os.path.join(os.getcwd(), "icons.qrc")

    if not os.path.exists(icons_dir):
        print(f"Error: icons directory not found: {icons_dir}")
        return False

    try:
        with open(qrc_file, 'w', encoding='utf-8') as f:
            f.write('<!DOCTYPE RCC>\n')
            f.write('<RCC version="1.0">\n')
            f.write('    <qresource prefix="/icons">\n')

            # Add manifest
            manifest_path = os.path.join(icons_dir, "manifest.json")
            if os.path.exists(manifest_path):
                rel_path = os.path.join("assets", "icons", "manifest.json")
                f.write(f'        <file>{rel_path}</file>\n')

            # Add all icons
            for file in os.listdir(icons_dir):
                if file.endswith(('.svg', '.png', '.jpg', '.ico')):
                    rel_path = os.path.join("assets", "icons", file)
                    f.write(f'        <file>{rel_path}</file>\n')

            f.write('    </qresource>\n')
            f.write('</RCC>\n')

        print(f"QRC file generated: {qrc_file}")
        return True
    except Exception as e:
        print(f"Error generating .qrc file: {e}")
        return False

if __name__ == "__main__":
    print_separator()
    if compile_resources():
        print("Resources compiled successfully")
        sys.exit(0)
    else:
        print("Failed to compile resources")
        sys.exit(1)
