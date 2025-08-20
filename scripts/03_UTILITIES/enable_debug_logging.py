#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Enable DEBUG Logging in GopiAI Modules
==========================================

This script patches the GopiAI modules to enable DEBUG logging specifically
for the chat widget and CrewAI client to capture detailed hang debugging info.
"""

import os
import sys
from pathlib import Path

def patch_chat_widget_for_debug():
    """Add DEBUG logging to chat widget"""
    
    chat_widget_path = Path("GopiAI-UI/gopiai/ui/components/chat_widget.py")
    if not chat_widget_path.exists():
        print(f"❌ Chat widget not found: {chat_widget_path}")
        return False
    
    # Read current content
    with open(chat_widget_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already patched
    if "logging.basicConfig(level=logging.DEBUG)" in content:
        print("✅ Chat widget already has DEBUG logging enabled")
        return True
    
    # Add DEBUG logging setup
    debug_patch = """
# DEBUG LOGGING PATCH - Added for hang diagnosis
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
print("🔧 DEBUG logging enabled for chat_widget.py")

"""
    
    # Insert after imports (find first class definition)
    lines = content.split('\n')
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('class ') and 'ChatWidget' in line:
            insert_pos = i
            break
    
    if insert_pos > 0:
        lines.insert(insert_pos, debug_patch)
        new_content = '\n'.join(lines)
        
        # Backup original
        backup_path = chat_widget_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Write patched version
        with open(chat_widget_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Chat widget patched with DEBUG logging")
        print(f"📁 Backup saved to: {backup_path}")
        return True
    else:
        print("❌ Could not find insertion point in chat widget")
        return False

def patch_crewai_client_for_debug():
    """Add DEBUG logging to CrewAI client"""
    
    client_path = Path("GopiAI-UI/gopiai/ui/components/crewai_client.py")
    if not client_path.exists():
        print(f"❌ CrewAI client not found: {client_path}")
        return False
    
    # Read current content
    with open(client_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already patched
    if "logging.basicConfig(level=logging.DEBUG)" in content:
        print("✅ CrewAI client already has DEBUG logging enabled")
        return True
    
    # Add DEBUG logging and detailed request logging
    debug_patch = """
# DEBUG LOGGING PATCH - Added for hang diagnosis
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
print("🔧 DEBUG logging enabled for crewai_client.py")

"""
    
    # Also patch the process_request method to add timing
    timing_patch = '''
        logger.debug(f"🕐 Starting request to {self.base_url}/api/process")
        logger.debug(f"📤 Request payload: {{'message': '{message[:100]}...', 'force_crewai': {False}}}")
        start_time = time.time()
        '''
    
    # Insert debug setup after imports
    lines = content.split('\n')
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('class ') and 'CrewAIClient' in line:
            insert_pos = i
            break
    
    if insert_pos > 0:
        lines.insert(insert_pos, debug_patch)
        
        # Also add timing to process_request method
        for i, line in enumerate(lines):
            if 'timeout=60' in line and 'requests.post' in lines[i-5:i+1]:
                lines.insert(i-1, timing_patch)
                # Add timing after request
                for j in range(i+5, min(i+15, len(lines))):
                    if 'if response.status_code == 200:' in lines[j]:
                        timing_end = '        elapsed = time.time() - start_time\n        logger.debug(f"⏱️ Request completed in {elapsed:.2f}s")'
                        lines.insert(j, timing_end)
                        break
                break
        
        new_content = '\n'.join(lines)
        
        # Backup original
        backup_path = client_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Write patched version
        with open(client_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ CrewAI client patched with DEBUG logging")
        print(f"📁 Backup saved to: {backup_path}")
        return True
    else:
        print("❌ Could not find insertion point in CrewAI client")
        return False

def restore_original_files():
    """Restore original files from backups"""
    
    files_to_restore = [
        "GopiAI-UI/gopiai/ui/components/chat_widget.py",
        "GopiAI-UI/gopiai/ui/components/crewai_client.py"
    ]
    
    restored = 0
    for file_path in files_to_restore:
        original_path = Path(file_path)
        backup_path = original_path.with_suffix('.py.backup')
        
        if backup_path.exists():
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(original_path, 'w', encoding='utf-8') as f:
                f.write(content)
            backup_path.unlink()  # Remove backup
            print(f"✅ Restored: {original_path}")
            restored += 1
        else:
            print(f"⚠️ No backup found for: {original_path}")
    
    print(f"📁 Restored {restored} files")

def main():
    """Main function"""
    
    print("🔧 GopiAI DEBUG Logging Patcher")
    print("="*50)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--restore':
        print("🔄 Restoring original files...")
        restore_original_files()
        return
    
    print("This script will patch GopiAI modules to enable DEBUG logging")
    print("Use --restore to restore original files")
    print("="*50)
    
    # Patch modules
    success_count = 0
    
    if patch_chat_widget_for_debug():
        success_count += 1
    
    if patch_crewai_client_for_debug():
        success_count += 1
    
    print("="*50)
    if success_count > 0:
        print(f"✅ Successfully patched {success_count} modules with DEBUG logging")
        print("💡 Now run GopiAI-UI to see detailed debug output")
        print("💡 Use 'python enable_debug_logging.py --restore' to undo changes")
    else:
        print("❌ No modules were successfully patched")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
