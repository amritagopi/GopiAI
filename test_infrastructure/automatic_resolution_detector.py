#!/usr/bin/env python3
"""
Automatic Resolution Detection System for Known Issues

This module provides automatic detection of when known issues have been resolved
by monitoring test results and automatically updating issue status when bugs are fixed.

Key features:
- Continuous monitoring of test results for known issues
- Automatic status updates when resolution threshold is met
- Smart detection of false positives
- Integration with CI/CD pipelines
- Notification system for resolved issues
"""

import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sqlite3
import threading
import logging

from known_issues_manager import KnownIssuesManager, IssueStatus, IssuePriority, KnownIssue


@dataclass
class ResolutionEvent:
    """Represents a resolution event for a known issue."""
    issue_id: str
    timestamp: str
    previous_status: str
    new_status: str
    resolution_percentage: float
    confidence_score: float
    test_results: Dict[str, int]
    verification_runs: int
    auto_resolved: bool
    notes: str


@dataclass
class MonitoringConfig:
    """Configuration for automatic resolution monitoring."""
    resolution_threshold: float = 95.0  # Percentage of tests that must pass
    confidence_threshold: float = 0.8   # Confidence score threshold
    verification_runs: int = 3           # Number of consecutive successful runs required
    monitoring_interval: int = 300       # Seconds between checks
    false_positive_protection: bool = True
    notification_enabled: bool = True
    auto_resolve_enabled: bool = True


class AutomaticResolutionDetector:
    """Detects and handles automatic resolution of known issues."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues_manager = KnownIssuesManager(project_root)
        
        # Configuration
        self.config = self._load_config()
        
        # Database for tracking resolution events
        self.resolution_db = self.issues_manager.issues_dir / "resolution_events.db"
        self._init_resolution_database()
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Setup logging
        self.logger = self._setup_logging()
        
    def _load_config(self) -> MonitoringConfig:
        """Load monitoring configuration."""
        config_file = self.issues_manager.issues_dir / "monitoring_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                return MonitoringConfig(**config_data)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}, using defaults")
        
        # Save default config
        config = MonitoringConfig()
        self._save_config(config)
        return config
    
    def _save_config(self, config: MonitoringConfig):
        """Save monitoring configuration."""
        config_file = self.issues_manager.issues_dir / "monitoring_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(asdict(config), f, indent=2)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for resolution detector."""
        logger = logging.getLogger("resolution_detector")
        logger.setLevel(logging.INFO)
        
        # File handler
        log_file = self.issues_manager.issues_dir / "resolution_detector.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _init_resolution_database(self):
        """Initialize database for tracking resolution events."""
        with sqlite3.connect(self.resolution_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS resolution_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    previous_status TEXT,
                    new_status TEXT,
                    resolution_percentage REAL,
                    confidence_score REAL,
                    test_results TEXT,
                    verification_runs INTEGER,
                    auto_resolved BOOLEAN,
                    notes TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS verification_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    test_results TEXT,
                    pass_percentage REAL,
                    consecutive_successes INTEGER
                )
            """)
            
            conn.commit()
    
    def check_for_resolutions(self) -> List[ResolutionEvent]:
        """Check all active issues for potential resolutions."""
        self.logger.info("Starting resolution check...")
        
        active_issues = (
            self.issues_manager.get_issues_by_status(IssueStatus.OPEN) +
            self.issues_manager.get_issues_by_status(IssueStatus.IN_PROGRESS)
        )
        
        resolution_events = []
        
        for issue in active_issues:
            try:
                event = self._check_issue_resolution(issue)
                if event:
                    resolution_events.append(event)
                    self._save_resolution_event(event)
                    
                    if event.auto_resolved:
                        self.logger.info(f"Auto-resolved issue {issue.issue_id}")
                        self._notify_resolution(event)
            
            except Exception as e:
                self.logger.error(f"Error checking issue {issue.issue_id}: {e}")
        
        return resolution_events
    
    def _check_issue_resolution(self, issue: KnownIssue) -> Optional[ResolutionEvent]:
        """Check if a specific issue should be resolved."""
        if not issue.affected_tests:
            return None
        
        # Run tests for this issue
        test_results = self._run_issue_tests(issue)
        
        if not test_results:
            return None
        
        # Calculate resolution percentage
        total_tests = test_results.get("total", 0)
        passing_tests = test_results.get("passed", 0)
        
        if total_tests == 0:
            return None
        
        resolution_percentage = (passing_tests / total_tests) * 100
        
        # Check if meets resolution threshold
        if resolution_percentage < self.config.resolution_threshold:
            return None
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(issue, test_results)
        
        if confidence_score < self.config.confidence_threshold:
            self.logger.info(f"Issue {issue.issue_id} meets threshold but confidence too low: {confidence_score}")
            return None
        
        # Check verification history if false positive protection is enabled
        if self.config.false_positive_protection:
            verification_count = self._get_verification_count(issue.issue_id, resolution_percentage)
            
            if verification_count < self.config.verification_runs:
                self.logger.info(f"Issue {issue.issue_id} needs more verification runs: {verification_count}/{self.config.verification_runs}")
                self._record_verification(issue.issue_id, test_results, resolution_percentage)
                return None
        
        # Create resolution event
        event = ResolutionEvent(
            issue_id=issue.issue_id,
            timestamp=datetime.now().isoformat(),
            previous_status=issue.status.value,
            new_status=IssueStatus.RESOLVED.value,
            resolution_percentage=resolution_percentage,
            confidence_score=confidence_score,
            test_results=test_results,
            verification_runs=self._get_verification_count(issue.issue_id, resolution_percentage),
            auto_resolved=self.config.auto_resolve_enabled,
            notes=f"Auto-resolved: {resolution_percentage:.1f}% tests passing with {confidence_score:.2f} confidence"
        )
        
        # Actually update the issue if auto-resolve is enabled
        if self.config.auto_resolve_enabled:
            success = self.issues_manager.update_issue_status(
                issue.issue_id,
                IssueStatus.RESOLVED,
                event.notes
            )
            
            if not success:
                self.logger.error(f"Failed to update issue {issue.issue_id} status")
                event.auto_resolved = False
        
        return event
    
    def _run_issue_tests(self, issue: KnownIssue) -> Optional[Dict[str, int]]:
        """Run tests for a specific issue."""
        if not issue.affected_tests:
            return None
        
        try:
            # Create temporary test list file
            temp_file = self.issues_manager.issues_dir / f"temp_tests_{issue.issue_id}.txt"
            with open(temp_file, 'w') as f:
                for test_name in issue.affected_tests:
                    f.write(f"{test_name}\n")
            
            # Run pytest with JSON output
            json_file = self.issues_manager.issues_dir / f"temp_results_{issue.issue_id}.json"
            
            cmd = [
                "python", "-m", "pytest",
                "--tb=short", "-q",
                "--json-report", f"--json-report-file={json_file}",
                "--maxfail=100"  # Don't stop on first failure
            ]
            
            # Add test files
            test_files = set()
            for test_name in issue.affected_tests:
                if "::" in test_name:
                    test_file = test_name.split("::")[0]
                    if Path(test_file).exists():
                        test_files.add(test_file)
            
            if not test_files:
                return None
            
            cmd.extend(test_files)
            
            # Run tests with timeout
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            # Parse JSON results
            if json_file.exists():
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                
                summary = json_data.get("summary", {})
                
                test_results = {
                    "total": summary.get("total", 0),
                    "passed": summary.get("passed", 0),
                    "failed": summary.get("failed", 0),
                    "skipped": summary.get("skipped", 0),
                    "error": summary.get("error", 0)
                }
                
                # Clean up temp files
                temp_file.unlink(missing_ok=True)
                json_file.unlink(missing_ok=True)
                
                return test_results
            
            else:
                # Fallback: parse stdout
                lines = result.stdout.split('\n')
                for line in lines:
                    if "passed" in line and "failed" in line:
                        # Try to parse pytest summary line
                        # This is a simplified parser
                        parts = line.split()
                        passed = failed = skipped = 0
                        
                        for i, part in enumerate(parts):
                            if "passed" in part and i > 0:
                                passed = int(parts[i-1])
                            elif "failed" in part and i > 0:
                                failed = int(parts[i-1])
                            elif "skipped" in part and i > 0:
                                skipped = int(parts[i-1])
                        
                        return {
                            "total": passed + failed + skipped,
                            "passed": passed,
                            "failed": failed,
                            "skipped": skipped,
                            "error": 0
                        }
                
                # If we can't parse, assume all tests failed
                return {
                    "total": len(issue.affected_tests),
                    "passed": 0,
                    "failed": len(issue.affected_tests),
                    "skipped": 0,
                    "error": 0
                }
        
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Test run for issue {issue.issue_id} timed out")
            return None
        except Exception as e:
            self.logger.error(f"Error running tests for issue {issue.issue_id}: {e}")
            return None
    
    def _calculate_confidence_score(self, issue: KnownIssue, test_results: Dict[str, int]) -> float:
        """Calculate confidence score for resolution."""
        confidence = 0.0
        
        # Base confidence from pass percentage
        total = test_results.get("total", 0)
        passed = test_results.get("passed", 0)
        
        if total > 0:
            pass_percentage = passed / total
            confidence += pass_percentage * 0.6  # 60% weight for pass rate
        
        # Bonus for high number of tests
        if total >= 5:
            confidence += 0.1
        elif total >= 10:
            confidence += 0.2
        
        # Penalty for skipped tests (might indicate environment issues)
        skipped = test_results.get("skipped", 0)
        if skipped > 0 and total > 0:
            skip_ratio = skipped / total
            confidence -= skip_ratio * 0.2
        
        # Bonus for issue priority (critical issues need higher confidence)
        if issue.priority == IssuePriority.CRITICAL:
            confidence -= 0.1  # Require higher confidence for critical issues
        elif issue.priority == IssuePriority.LOW:
            confidence += 0.1  # Lower confidence OK for low priority
        
        # Historical stability bonus
        verification_count = self._get_verification_count(issue.issue_id, pass_percentage * 100)
        if verification_count >= 2:
            confidence += min(verification_count * 0.05, 0.2)  # Up to 20% bonus
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _get_verification_count(self, issue_id: str, min_percentage: float) -> int:
        """Get number of consecutive verification runs above threshold."""
        with sqlite3.connect(self.resolution_db) as conn:
            cursor = conn.execute("""
                SELECT pass_percentage FROM verification_history 
                WHERE issue_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (issue_id, self.config.verification_runs))
            
            rows = cursor.fetchall()
            
            consecutive_count = 0
            for row in rows:
                if row[0] >= min_percentage:
                    consecutive_count += 1
                else:
                    break
            
            return consecutive_count
    
    def _record_verification(self, issue_id: str, test_results: Dict[str, int], pass_percentage: float):
        """Record verification run for an issue."""
        with sqlite3.connect(self.resolution_db) as conn:
            conn.execute("""
                INSERT INTO verification_history (
                    issue_id, timestamp, test_results, pass_percentage, consecutive_successes
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                issue_id,
                datetime.now().isoformat(),
                json.dumps(test_results),
                pass_percentage,
                self._get_verification_count(issue_id, pass_percentage)
            ))
            conn.commit()
    
    def _save_resolution_event(self, event: ResolutionEvent):
        """Save resolution event to database."""
        with sqlite3.connect(self.resolution_db) as conn:
            conn.execute("""
                INSERT INTO resolution_events (
                    issue_id, timestamp, previous_status, new_status,
                    resolution_percentage, confidence_score, test_results,
                    verification_runs, auto_resolved, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.issue_id, event.timestamp, event.previous_status,
                event.new_status, event.resolution_percentage, event.confidence_score,
                json.dumps(event.test_results), event.verification_runs,
                event.auto_resolved, event.notes
            ))
            conn.commit()
    
    def _notify_resolution(self, event: ResolutionEvent):
        """Send notification about resolved issue."""
        if not self.config.notification_enabled:
            return
        
        message = f"""
🎉 Known Issue Auto-Resolved!

Issue: {event.issue_id}
Resolution: {event.resolution_percentage:.1f}% tests passing
Confidence: {event.confidence_score:.2f}
Verification Runs: {event.verification_runs}
Timestamp: {event.timestamp}

{event.notes}
"""
        
        # Log notification
        self.logger.info(f"Resolution notification: {event.issue_id}")
        
        # Save notification to file
        notification_file = self.issues_manager.issues_dir / "resolution_notifications.log"
        with open(notification_file, 'a') as f:
            f.write(f"\n{datetime.now().isoformat()}: {message}\n")
        
        # TODO: Add email/Slack integration here
        print(message)
    
    def start_monitoring(self):
        """Start continuous monitoring for issue resolutions."""
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("Started automatic resolution monitoring")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        
        self.logger.info("Stopped automatic resolution monitoring")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self.check_for_resolutions()
                time.sleep(self.config.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    def get_resolution_history(self, issue_id: Optional[str] = None) -> List[ResolutionEvent]:
        """Get resolution history for all issues or specific issue."""
        with sqlite3.connect(self.resolution_db) as conn:
            if issue_id:
                cursor = conn.execute("""
                    SELECT * FROM resolution_events 
                    WHERE issue_id = ? 
                    ORDER BY timestamp DESC
                """, (issue_id,))
            else:
                cursor = conn.execute("""
                    SELECT * FROM resolution_events 
                    ORDER BY timestamp DESC
                """)
            
            events = []
            for row in cursor.fetchall():
                event = ResolutionEvent(
                    issue_id=row[1],
                    timestamp=row[2],
                    previous_status=row[3],
                    new_status=row[4],
                    resolution_percentage=row[5],
                    confidence_score=row[6],
                    test_results=json.loads(row[7]) if row[7] else {},
                    verification_runs=row[8],
                    auto_resolved=bool(row[9]),
                    notes=row[10]
                )
                events.append(event)
            
            return events
    
    def generate_resolution_report(self) -> Dict:
        """Generate comprehensive resolution report."""
        events = self.get_resolution_history()
        
        # Statistics
        total_events = len(events)
        auto_resolved = len([e for e in events if e.auto_resolved])
        manual_resolved = total_events - auto_resolved
        
        # Recent activity (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_events = [e for e in events if e.timestamp > week_ago]
        
        # Average confidence and resolution percentage
        if events:
            avg_confidence = sum(e.confidence_score for e in events) / len(events)
            avg_resolution = sum(e.resolution_percentage for e in events) / len(events)
        else:
            avg_confidence = avg_resolution = 0.0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_resolution_events": total_events,
            "auto_resolved_count": auto_resolved,
            "manual_resolved_count": manual_resolved,
            "recent_activity": len(recent_events),
            "average_confidence_score": avg_confidence,
            "average_resolution_percentage": avg_resolution,
            "monitoring_config": asdict(self.config),
            "recent_events": [asdict(e) for e in recent_events[:10]],
            "recommendations": self._generate_resolution_recommendations(events)
        }
        
        # Save report
        report_file = self.issues_manager.issues_dir / "resolution_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _generate_resolution_recommendations(self, events: List[ResolutionEvent]) -> List[str]:
        """Generate recommendations based on resolution history."""
        recommendations = []
        
        if not events:
            recommendations.append("No resolution events yet - system is ready to detect resolutions")
            return recommendations
        
        # Check auto-resolution rate
        auto_rate = len([e for e in events if e.auto_resolved]) / len(events)
        if auto_rate < 0.5:
            recommendations.append("Consider enabling auto-resolution for more efficient issue management")
        
        # Check confidence scores
        low_confidence = [e for e in events if e.confidence_score < 0.7]
        if len(low_confidence) > len(events) * 0.3:
            recommendations.append("Many resolutions have low confidence - consider adjusting thresholds")
        
        # Check verification runs
        insufficient_verification = [e for e in events if e.verification_runs < 2]
        if len(insufficient_verification) > len(events) * 0.2:
            recommendations.append("Consider increasing verification runs for more reliable detection")
        
        # Recent activity
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent = [e for e in events if e.timestamp > week_ago]
        if len(recent) > 5:
            recommendations.append("High resolution activity - great progress on fixing issues!")
        elif len(recent) == 0 and len(events) > 0:
            recommendations.append("No recent resolutions - check if monitoring is working correctly")
        
        return recommendations


def main():
    """Main function for testing automatic resolution detection."""
    detector = AutomaticResolutionDetector()
    
    print("🤖 Automatic Resolution Detection System")
    print("=" * 50)
    
    # Check for resolutions
    events = detector.check_for_resolutions()
    
    if events:
        print(f"\n🎉 Found {len(events)} resolution events:")
        for event in events:
            print(f"  {event.issue_id}: {event.resolution_percentage:.1f}% (confidence: {event.confidence_score:.2f})")
    else:
        print("\n✅ No issues ready for resolution")
    
    # Generate report
    report = detector.generate_resolution_report()
    print(f"\n📊 Resolution Report:")
    print(f"  Total Events: {report['total_resolution_events']}")
    print(f"  Auto-Resolved: {report['auto_resolved_count']}")
    print(f"  Recent Activity: {report['recent_activity']}")
    print(f"  Average Confidence: {report['average_confidence_score']:.2f}")
    
    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")


if __name__ == "__main__":
    main()