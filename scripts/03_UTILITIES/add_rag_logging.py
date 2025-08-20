#!/usr/bin/env python3
"""
🔧 Add Temporary RAG Logging

This script adds temporary logging breakpoints to key files to monitor RAG calls.
It modifies the files to add logging statements that will help verify 
whether RAG requests are being made during normal message flow.
"""

import os
import sys
import shutil
from pathlib import Path

def backup_file(file_path):
    """Create a backup of the original file"""
    backup_path = f"{file_path}.backup"
    if not os.path.exists(backup_path):
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
    else:
        print(f"ℹ️ Backup already exists: {backup_path}")

def restore_file(file_path):
    """Restore file from backup"""
    backup_path = f"{file_path}.backup"
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, file_path)
        print(f"✅ Restored from backup: {file_path}")
        return True
    else:
        print(f"❌ No backup found: {backup_path}")
        return False

def add_logging_to_gopiai_agent():
    """Add logging to the GopiAI agent's RAG functions"""
    agent_file = Path(__file__).parent / "rag_memory_system" / "txtchat_integration" / "gopiai_agent.py"
    
    if not agent_file.exists():
        print(f"❌ File not found: {agent_file}")
        return False
    
    print(f"🔧 Adding logging to: {agent_file}")
    backup_file(str(agent_file))
    
    # Read the file
    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add logging to _fetch_rag_context method
    old_fetch_method = """    def _fetch_rag_context(self, message: str) -> Optional[str]:
        \"\"\"Получение контекста из RAG сервера\"\"\"
        rag_config = self.config['rag']
        
        try:
            url = f"{rag_config['server_url']}/api/search\""""
    
    new_fetch_method = """    def _fetch_rag_context(self, message: str) -> Optional[str]:
        \"\"\"Получение контекста из RAG сервера\"\"\"
        rag_config = self.config['rag']
        
        # ===== TEMPORARY RAG LOGGING =====
        print(f"🔍 [RAG DEBUG] _fetch_rag_context called with message: '{message[:50]}...'")
        logger.critical(f"🔍 [RAG DEBUG] _fetch_rag_context called with message: '{message[:50]}...'")
        # ================================
        
        try:
            url = f"{rag_config['server_url']}/api/search"
            
            # ===== TEMPORARY RAG LOGGING =====
            print(f"🔍 [RAG DEBUG] About to make HTTP POST to: {url}")
            logger.critical(f"🔍 [RAG DEBUG] About to make HTTP POST to: {url}")
            # ================================"""
    
    # Replace the method
    content = content.replace(old_fetch_method, new_fetch_method)
    
    # Add logging after the HTTP request
    old_response_check = """            if response.status_code == 200:
                data = response.json()
                context = data.get('context')"""
    
    new_response_check = """            # ===== TEMPORARY RAG LOGGING =====
            print(f"🔍 [RAG DEBUG] HTTP POST completed, status: {response.status_code}")
            logger.critical(f"🔍 [RAG DEBUG] HTTP POST completed, status: {response.status_code}")
            # ================================
            
            if response.status_code == 200:
                data = response.json()
                context = data.get('context')
                
                # ===== TEMPORARY RAG LOGGING =====
                print(f"🔍 [RAG DEBUG] RAG response received, context length: {len(context) if context else 0}")
                logger.critical(f"🔍 [RAG DEBUG] RAG response received, context length: {len(context) if context else 0}")
                # ================================"""
    
    content = content.replace(old_response_check, new_response_check)
    
    # Write the modified file
    with open(agent_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Logging added to gopiai_agent.py")
    return True

def add_logging_to_chat_widget():
    """Add logging to the chat widget's RAG health check"""
    widget_file = Path(__file__).parent / "GopiAI-UI" / "gopiai" / "ui" / "components" / "chat_widget.py"
    
    if not widget_file.exists():
        print(f"❌ File not found: {widget_file}")
        return False
    
    print(f"🔧 Adding logging to: {widget_file}")
    backup_file(str(widget_file))
    
    # Read the file
    with open(widget_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add logging to RAG availability check
    old_rag_check = """        # Check RAG service
        try:
            response = requests.get("http://127.0.0.1:5051/api/health", timeout=2)
            self.rag_available = response.status_code == 200"""
    
    new_rag_check = """        # Check RAG service
        try:
            # ===== TEMPORARY RAG LOGGING =====
            print("🔍 [RAG DEBUG] Checking RAG service availability...")
            logger.critical("🔍 [RAG DEBUG] Checking RAG service availability...")
            # ================================
            
            response = requests.get("http://127.0.0.1:5051/api/health", timeout=2)
            self.rag_available = response.status_code == 200
            
            # ===== TEMPORARY RAG LOGGING =====
            print(f"🔍 [RAG DEBUG] RAG health check result: {self.rag_available}")
            logger.critical(f"🔍 [RAG DEBUG] RAG health check result: {self.rag_available}")
            # ================================"""
    
    content = content.replace(old_rag_check, new_rag_check)
    
    # Write the modified file
    with open(widget_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Logging added to chat_widget.py")
    return True

def restore_all_files():
    """Restore all modified files from backups"""
    files_to_restore = [
        Path(__file__).parent / "rag_memory_system" / "txtchat_integration" / "gopiai_agent.py",
        Path(__file__).parent / "GopiAI-UI" / "gopiai" / "ui" / "components" / "chat_widget.py"
    ]
    
    restored_count = 0
    for file_path in files_to_restore:
        if restore_file(str(file_path)):
            restored_count += 1
    
    print(f"✅ Restored {restored_count} files")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        print("🔄 Restoring all files from backups...")
        restore_all_files()
        print("✅ All files restored!")
        return
    
    print("🔧 Adding temporary RAG logging to key files...")
    print("=" * 60)
    print("This will add debug logging to monitor RAG calls")
    print("Run with 'restore' argument to undo changes")
    print("=" * 60)
    
    success_count = 0
    
    # Add logging to files
    if add_logging_to_gopiai_agent():
        success_count += 1
    
    if add_logging_to_chat_widget():
        success_count += 1
    
    print(f"\n✅ Logging added to {success_count} files")
    print("\nNow run your application and watch for RAG debug messages:")
    print("🔍 [RAG DEBUG] messages will appear in console output")
    print("\nTo restore original files: python add_rag_logging.py restore")

if __name__ == "__main__":
    main()
