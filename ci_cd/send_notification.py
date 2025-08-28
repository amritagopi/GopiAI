#!/usr/bin/env python3
"""
Simple notification sender script for CI/CD integration
Wrapper around the notification system for easy command-line usage
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

from ci_cd.notification_system import NotificationSystem, TestResult
from datetime import datetime


def load_last_execution_result() -> TestResult:
    """Load the last test execution result"""
    result_file = Path('ci_cd/last_execution_result.json')
    
    if result_file.exists():
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return TestResult(**data)
        except Exception as e:
            print(f"Warning: Could not load last execution result: {e}")
    
    # Return default result
    return TestResult(
        timestamp=datetime.now().isoformat(),
        environment="unknown",
        total_tests=0,
        passed=0,
        failed=0,
        skipped=0,
        errors=0,
        duration=0.0,
        coverage_percentage=0.0,
        exit_code=1
    )


def create_result_from_args(args) -> TestResult:
    """Create TestResult from command line arguments"""
    exit_code = 0 if args.status == 'success' else 1
    
    return TestResult(
        timestamp=datetime.now().isoformat(),
        environment=args.environment,
        total_tests=getattr(args, 'total_tests', 0),
        passed=getattr(args, 'passed', 0),
        failed=getattr(args, 'failed', 0 if args.status == 'success' else 1),
        skipped=getattr(args, 'skipped', 0),
        errors=getattr(args, 'errors', 0),
        duration=getattr(args, 'duration', 0.0),
        coverage_percentage=getattr(args, 'coverage', 0.0),
        exit_code=exit_code,
        build_number=getattr(args, 'build_number', None),
        commit_hash=getattr(args, 'commit_hash', None),
        branch=getattr(args, 'branch', None),
        report_url=getattr(args, 'report_url', None)
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Send CI/CD notifications for GopiAI test results'
    )
    
    # Required arguments
    parser.add_argument('--type', required=True,
                       choices=['test_completion', 'deployment', 'pipeline'],
                       help='Type of notification to send')
    parser.add_argument('--status', required=True,
                       choices=['success', 'failure', 'unstable'],
                       help='Status of the operation')
    parser.add_argument('--environment', required=True,
                       help='Target environment (development, staging, production)')
    
    # Optional arguments
    parser.add_argument('--build-number', help='Build number')
    parser.add_argument('--commit-hash', help='Git commit hash')
    parser.add_argument('--branch', help='Git branch name')
    parser.add_argument('--report-url', help='URL to detailed report')
    parser.add_argument('--config', help='Notification configuration file')
    parser.add_argument('--use-last-result', action='store_true',
                       help='Use last test execution result')
    
    # Test result arguments (for manual specification)
    parser.add_argument('--total-tests', type=int, help='Total number of tests')
    parser.add_argument('--passed', type=int, help='Number of passed tests')
    parser.add_argument('--failed', type=int, help='Number of failed tests')
    parser.add_argument('--skipped', type=int, help='Number of skipped tests')
    parser.add_argument('--errors', type=int, help='Number of test errors')
    parser.add_argument('--duration', type=float, help='Test execution duration')
    parser.add_argument('--coverage', type=float, help='Code coverage percentage')
    
    # Notification channel overrides
    parser.add_argument('--email-only', action='store_true',
                       help='Send only email notifications')
    parser.add_argument('--slack-only', action='store_true',
                       help='Send only Slack notifications')
    parser.add_argument('--discord-only', action='store_true',
                       help='Send only Discord notifications')
    parser.add_argument('--teams-only', action='store_true',
                       help='Send only Teams notifications')
    
    # Debug options
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be sent without actually sending')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    try:
        # Initialize notification system
        notifier = NotificationSystem(args.config)
        
        # Get test result
        if args.use_last_result:
            result = load_last_execution_result()
            # Override with command line values if provided
            if args.build_number:
                result.build_number = args.build_number
            if args.commit_hash:
                result.commit_hash = args.commit_hash
            if args.branch:
                result.branch = args.branch
            if args.report_url:
                result.report_url = args.report_url
        else:
            result = create_result_from_args(args)
        
        # Override notification channels if specified
        if args.email_only:
            notifier.config.slack = None
            notifier.config.discord = None
            notifier.config.teams = None
            notifier.config.webhooks = None
        elif args.slack_only:
            notifier.config.email = None
            notifier.config.discord = None
            notifier.config.teams = None
            notifier.config.webhooks = None
        elif args.discord_only:
            notifier.config.email = None
            notifier.config.slack = None
            notifier.config.teams = None
            notifier.config.webhooks = None
        elif args.teams_only:
            notifier.config.email = None
            notifier.config.slack = None
            notifier.config.discord = None
            notifier.config.webhooks = None
        
        if args.dry_run:
            print("DRY RUN - Would send the following notification:")
            print(f"Type: {args.type}")
            print(f"Status: {args.status}")
            print(f"Environment: {args.environment}")
            print(f"Result: {result}")
            print("\nChannels that would be notified:")
            if notifier.config.email and notifier.config.email.get('enabled'):
                print("- Email")
            if notifier.config.slack and notifier.config.slack.get('enabled'):
                print("- Slack")
            if notifier.config.discord and notifier.config.discord.get('enabled'):
                print("- Discord")
            if notifier.config.teams and notifier.config.teams.get('enabled'):
                print("- Microsoft Teams")
            if notifier.config.webhooks:
                print(f"- {len(notifier.config.webhooks)} webhook(s)")
            return
        
        # Send notifications
        success_count, total_channels = notifier.send_test_results(result, args.type)
        
        print(f"✅ Successfully sent notifications to {success_count}/{total_channels} channels")
        
        if success_count == 0:
            print("❌ No notifications were sent successfully")
            sys.exit(1)
        elif success_count < total_channels:
            print(f"⚠️  Some notifications failed ({total_channels - success_count} failed)")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error sending notifications: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()