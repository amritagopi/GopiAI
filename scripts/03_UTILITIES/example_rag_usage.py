#!/usr/bin/env python3
"""
Example usage of the get_rag_context function.

This demonstrates how to use the RAG context retrieval helper function
in various scenarios within the GopiAI project.
"""

import sys
import os

# Add GopiAI-App to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'GopiAI-App'))

def example_basic_usage():
    """Example of basic RAG context retrieval."""
    print("🔍 Example 1: Basic RAG Context Retrieval")
    print("=" * 50)
    
    try:
        from gopiai.app.utils.common import get_rag_context
        
        # Example query
        query = "How to configure CrewAI agents?"
        
        # Get RAG context
        context = get_rag_context(query, max_results=3)
        
        if context:
            print(f"✅ Query: {query}")
            print(f"📊 Context length: {len(context)} characters")
            print(f"🔗 Context preview:")
            print(context[:300] + "..." if len(context) > 300 else context)
        else:
            print(f"⚠️ No context found for query: {query}")
            print("💡 This is expected if the RAG server is not running")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Using fallback implementation...")
        
        # Fallback implementation for demonstration
        import requests
        
        def get_rag_context_fallback(query: str, max_results: int = 3) -> str:
            try:
                response = requests.post(
                    "http://127.0.0.1:5051/api/search",
                    json={"query": query, "max_results": max_results},
                    timeout=4
                )
                
                if response.status_code == 200:
                    data = response.json()
                    context_items = data.get("context", [])
                    
                    if isinstance(context_items, list):
                        return "\n".join(context_items)
                    else:
                        return str(context_items)
                else:
                    return ""
            except requests.exceptions.RequestException:
                return ""
        
        context = get_rag_context_fallback(query, max_results=3)
        
        if context:
            print(f"✅ Fallback worked! Context length: {len(context)} characters")
        else:
            print("⚠️ No context retrieved - RAG server might be unavailable")

def example_chat_integration():
    """Example of how to integrate RAG context in a chat flow."""
    print("\n🔍 Example 2: Chat Integration with RAG Context")
    print("=" * 50)
    
    # Simulate a chat scenario
    user_message = "What are the best practices for agent memory?"
    
    try:
        from gopiai.app.utils.common import get_rag_context
        
        # Get relevant context
        context = get_rag_context(user_message, max_results=5)
        
        # Create enhanced message with context
        if context:
            enhanced_message = f"""Based on previous knowledge:
{context}

Current question: {user_message}"""
            
            print(f"✅ Original message: {user_message}")
            print(f"📈 Enhanced message length: {len(enhanced_message)} characters")
            print(f"🔗 Enhancement preview:")
            print(enhanced_message[:400] + "..." if len(enhanced_message) > 400 else enhanced_message)
        else:
            enhanced_message = user_message
            print(f"ℹ️ No context available, using original message")
            
    except Exception as e:
        print(f"❌ Error in chat integration: {e}")

def example_batch_queries():
    """Example of processing multiple queries."""
    print("\n🔍 Example 3: Batch Query Processing")
    print("=" * 50)
    
    queries = [
        "How to set up CrewAI?",
        "What is RAG memory?",
        "Python agent configuration",
        "Best practices for AI workflows"
    ]
    
    try:
        from gopiai.app.utils.common import get_rag_context
        
        for i, query in enumerate(queries, 1):
            print(f"\n{i}. Query: {query}")
            
            context = get_rag_context(query, max_results=2)
            
            if context:
                print(f"   ✅ Found context ({len(context)} chars)")
            else:
                print("   ⚠️ No context found")
                
    except Exception as e:
        print(f"❌ Error in batch processing: {e}")

def example_different_result_counts():
    """Example of using different max_results parameters."""
    print("\n🔍 Example 4: Different Result Counts")
    print("=" * 50)
    
    query = "Agent configuration examples"
    
    try:
        from gopiai.app.utils.common import get_rag_context
        
        for max_results in [1, 3, 5, 10]:
            context = get_rag_context(query, max_results=max_results)
            
            print(f"Max results: {max_results:2d} → Context length: {len(context):4d} characters")
            
    except Exception as e:
        print(f"❌ Error testing different result counts: {e}")

def example_error_handling():
    """Example of proper error handling."""
    print("\n🔍 Example 5: Error Handling")
    print("=" * 50)
    
    try:
        from gopiai.app.utils.common import get_rag_context
        
        # Test with empty query
        context = get_rag_context("", max_results=3)
        print(f"Empty query result: '{context}' (length: {len(context)})")
        
        # Test with very long query
        long_query = "This is a very long query " * 50
        context = get_rag_context(long_query, max_results=3)
        print(f"Long query result length: {len(context)} characters")
        
        # Test with special characters
        special_query = "Агенты и конфигурация 中文测试 🤖"
        context = get_rag_context(special_query, max_results=3)
        print(f"Special chars query result length: {len(context)} characters")
        
    except Exception as e:
        print(f"❌ Error in error handling test: {e}")

def main():
    """Main example function."""
    print("🧪 RAG Context Retrieval Examples")
    print("=" * 60)
    print("This demonstrates the get_rag_context function usage")
    print()
    
    # Run all examples
    example_basic_usage()
    example_chat_integration()
    example_batch_queries()
    example_different_result_counts()
    example_error_handling()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print()
    print("💡 Integration tips:")
    print("   - Always check if context is empty before using")
    print("   - Use appropriate max_results for your use case")
    print("   - The function gracefully handles RAG server unavailability")
    print("   - Context can be appended to user messages for better AI responses")

if __name__ == "__main__":
    main()
