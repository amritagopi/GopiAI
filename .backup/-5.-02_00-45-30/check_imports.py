print("Checking imports...")

try:
    import app.utils.theme_manager
    print("Successfully imported theme_manager")
except Exception as e:
    print(f"Error importing theme_manager: {e}")

try:
    import app.utils.theme_utils
    print("Successfully imported theme_utils")
except Exception as e:
    print(f"Error importing theme_utils: {e}")

print("Import checks complete")
