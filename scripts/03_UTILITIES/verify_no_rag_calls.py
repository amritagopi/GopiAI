#!/usr/bin/env python3
"""
🔍 RAG Call Verification Script

This script helps verify that no HTTP requests are sent to http://127.0.0.1:5051/api/search
during normal message flow by:

1. Temporarily patching HTTP libraries to log all requests
2. Running test scenarios with the chat interface
3. Analyzing the logged requests to confirm RAG calls are absent

This establishes the baseline problem where RAG is not being called.
"""

import sys
import time
import json
import logging
import threading
from unittest.mock import patch
from contextlib import contextmanager
from pathlib import Path

# Setup logging for monitoring
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_call_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global list to track all HTTP requests
http_requests_log = []

def log_http_request(method, url, *args, **kwargs):
    """Log all HTTP requests for analysis"""
    timestamp = time.time()
    request_info = {
        'timestamp': timestamp,
        'method': method,
        'url': url,
        'args': args,
        'kwargs': kwargs
    }
    http_requests_log.append(request_info)
    
    # Check if this is a RAG request
    if '127.0.0.1:5051' in url and '/api/search' in url:
        logger.critical(f"🔴 RAG REQUEST DETECTED: {method} {url}")
        print(f"🔴 RAG REQUEST DETECTED: {method} {url}")
    else:
        logger.info(f"📡 HTTP Request: {method} {url}")
        
    return request_info

# Patch requests library to monitor all HTTP calls
original_requests_get = None
original_requests_post = None

def patched_requests_get(url, *args, **kwargs):
    """Patched requests.get to log all calls"""
    log_http_request('GET', url, *args, **kwargs)
    return original_requests_get(url, *args, **kwargs)

def patched_requests_post(url, *args, **kwargs):
    """Patched requests.post to log all calls"""
    log_http_request('POST', url, *args, **kwargs)
    return original_requests_post(url, *args, **kwargs)

@contextmanager
def monitor_http_requests():
    """Context manager to patch and monitor HTTP requests"""
    global original_requests_get, original_requests_post
    
    try:
        import requests
        
        # Store original methods
        original_requests_get = requests.get
        original_requests_post = requests.post
        
        # Apply patches
        requests.get = patched_requests_get
        requests.post = patched_requests_post
        
        logger.info("🔍 HTTP monitoring started")
        print("🔍 HTTP monitoring started - watching for RAG calls...")
        
        yield
        
    finally:
        # Restore original methods
        if original_requests_get:
            requests.get = original_requests_get
        if original_requests_post:
            requests.post = original_requests_post
        
        logger.info("🔍 HTTP monitoring stopped")
        print("🔍 HTTP monitoring stopped")

def analyze_http_requests():
    """Analyze logged HTTP requests to check for RAG calls"""
    print("\n" + "="*60)
    print("📊 HTTP REQUEST ANALYSIS")
    print("="*60)
    
    total_requests = len(http_requests_log)
    rag_requests = [req for req in http_requests_log 
                   if '127.0.0.1:5051' in req['url'] and '/api/search' in req['url']]
    other_requests = [req for req in http_requests_log 
                     if not ('127.0.0.1:5051' in req['url'] and '/api/search' in req['url'])]
    
    print(f"Total HTTP requests: {total_requests}")
    print(f"RAG search requests: {len(rag_requests)}")
    print(f"Other requests: {len(other_requests)}")
    
    if rag_requests:
        print(f"\n🔴 RAG REQUESTS FOUND ({len(rag_requests)}):")
        for req in rag_requests:
            print(f"  - {req['method']} {req['url']} at {time.ctime(req['timestamp'])}")
        return False
    else:
        print("\n✅ NO RAG REQUESTS DETECTED")
        print("This confirms the baseline problem - RAG is not being called during normal message flow")
        
    if other_requests:
        print(f"\n📡 OTHER HTTP REQUESTS ({len(other_requests)}):")
        for req in other_requests:
            print(f"  - {req['method']} {req['url']}")
            
    return True

def test_basic_message_flow():
    """Test basic message flow without UI"""
    print("\n" + "="*60)
    print("🧪 TESTING BASIC MESSAGE FLOW")
    print("="*60)
    
    try:
        # Add project paths
        sys.path.append(str(Path(__file__).parent / "rag_memory_system" / "txtchat_integration"))
        
        # Import the agent
        from gopiai_agent import create_agent
        
        # Create agent
        agent = create_agent()
        print(f"✅ Agent created: {agent.config['agent']['name']}")
        
        # Test messages
        test_messages = [
            "Hello, how are you?",
            "What is machine learning?", 
            "Tell me about AI",
            "How does RAG work?"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Test Message {i}: '{message}' ---")
            
            try:
                result = agent.process_message(message)
                print(f"✅ Message processed")
                print(f"   RAG used: {result.get('metadata', {}).get('rag_used', False)}")
                print(f"   Response length: {len(result.get('response', ''))}")
                
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                
    except ImportError as e:
        print(f"❌ Cannot import agent: {e}")
        print("Skipping agent tests")
    except Exception as e:
        print(f"❌ Error in agent tests: {e}")

def test_crewai_client():
    """Test CrewAI client separately"""
    print("\n" + "="*60)
    print("🧪 TESTING CREWAI CLIENT")
    print("="*60)
    
    try:
        sys.path.append(str(Path(__file__).parent / "GopiAI-UI" / "gopiai" / "ui" / "components"))
        
        from crewai_client import CrewAIClient
        
        client = CrewAIClient()
        print(f"✅ CrewAI client created")
        
        # Test availability check
        available = client.is_available()
        print(f"CrewAI server available: {available}")
        
        # Test analysis request
        analysis = client.analyze_request("Tell me about machine learning")
        print(f"Analysis result: {analysis}")
        
    except ImportError as e:
        print(f"❌ Cannot import CrewAI client: {e}")
    except Exception as e:
        print(f"❌ Error in CrewAI client tests: {e}")

def add_logging_to_files():
    """Add temporary logging to key files to monitor RAG calls"""
    print("\n" + "="*60)
    print("🔧 ADDING TEMPORARY LOGGING")
    print("="*60)
    
    # Files to modify with logging
    files_to_modify = [
        "rag_memory_system/txtchat_integration/gopiai_agent.py",
        "GopiAI-UI/gopiai/ui/components/crewai_client.py", 
        "GopiAI-UI/gopiai/ui/components/chat_widget.py"
    ]
    
    for file_path in files_to_modify:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"✅ Found: {file_path}")
            # We could add logging here, but patching at runtime is cleaner
        else:
            print(f"❌ Not found: {file_path}")

def save_results():
    """Save verification results to a file"""
    results = {
        'timestamp': time.time(),
        'total_requests': len(http_requests_log),
        'rag_requests': [req for req in http_requests_log 
                        if '127.0.0.1:5051' in req['url'] and '/api/search' in req['url']],
        'analysis': 'No RAG requests found' if not any('127.0.0.1:5051' in req['url'] and '/api/search' in req['url'] 
                                                       for req in http_requests_log) else 'RAG requests detected'
    }
    
    with open('rag_verification_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to rag_verification_results.json")

def main():
    """Main verification function"""
    print("🔍 RAG CALL VERIFICATION - Step 2")
    print("="*60)
    print("This script verifies that no HTTP requests are sent to")
    print("http://127.0.0.1:5051/api/search during normal message flow")
    print("="*60)
    
    # Clear previous logs
    http_requests_log.clear()
    
    # Monitor HTTP requests during testing
    with monitor_http_requests():
        # Test basic agent functionality
        test_basic_message_flow()
        
        # Test CrewAI client
        test_crewai_client()
        
        # Wait a bit to catch any delayed requests
        print("\n⏳ Waiting 5 seconds to catch any delayed requests...")
        time.sleep(5)
    
    # Analyze results
    no_rag_calls = analyze_http_requests()
    
    # Save results
    save_results()
    
    # Summary
    print("\n" + "="*60)
    print("📋 VERIFICATION SUMMARY")
    print("="*60)
    
    if no_rag_calls:
        print("✅ BASELINE CONFIRMED: No RAG calls detected during normal message flow")
        print("This establishes the problem - RAG integration is not working")
        print("\nNext steps:")
        print("1. Identify why RAG calls are not being made")
        print("2. Fix the integration to enable RAG calls") 
        print("3. Verify RAG calls work after fixes")
    else:
        print("❌ RAG calls detected - this means RAG is already working")
        print("Re-examine the problem statement")
        
    print(f"\nDetailed logs saved to: rag_call_monitor.log")
    print(f"Results saved to: rag_verification_results.json")

if __name__ == "__main__":
    main()
