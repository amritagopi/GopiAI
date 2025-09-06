#!/usr/bin/env python3
"""
End-to-end tests for GopiAI-UI module.

Tests complete user scenarios from UI interaction to backend response.
This file now redirects to the comprehensive E2E tests in tests/e2e/
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the comprehensive E2E tests
from tests.e2e.test_complete_scenarios import (
    TestCompleteConversationFlow,
    TestMemoryPersistence,
    TestServiceRecovery,
    TestMultipleUsers
)


class TestUserScenarios:
    """Test complete user scenarios - redirects to comprehensive E2E tests."""
    
    @pytest.mark.e2e
    @pytest.mark.requires_crewai
    @pytest.mark.requires_display
    def test_complete_conversation_flow(self, e2e_environment):
        """Test complete conversation flow from UI to AI response."""
        # Use the comprehensive E2E test implementation
        test_instance = TestCompleteConversationFlow()
        test_instance.test_full_conversation_cycle(e2e_environment)
    
    @pytest.mark.e2e
    @pytest.mark.requires_display
    def test_model_switching_scenario(self, e2e_environment):
        """Test model switching through UI."""
        # Use the comprehensive E2E test implementation
        test_instance = TestCompleteConversationFlow()
        test_instance.test_conversation_with_model_switching(e2e_environment)
    
    @pytest.mark.e2e
    @pytest.mark.requires_display
    def test_memory_persistence_scenario(self, e2e_environment):
        """Test memory persistence across sessions."""
        # Use the comprehensive E2E test implementation
        test_instance = TestMemoryPersistence()
        test_instance.test_context_persistence_across_sessions(e2e_environment)
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_service_recovery_scenario(self, e2e_environment):
        """Test service recovery after failures."""
        # Use the comprehensive E2E test implementation
        test_instance = TestServiceRecovery()
        test_instance.test_crewai_server_recovery(e2e_environment)
    
    @pytest.mark.e2e
    @pytest.mark.load_test
    def test_multiple_users_scenario(self, e2e_environment):
        """Test multiple concurrent users."""
        # Use the comprehensive E2E test implementation
        test_instance = TestMultipleUsers()
        test_instance.test_concurrent_conversations(e2e_environment)


if __name__ == "__main__":
    pytest.main([__file__])