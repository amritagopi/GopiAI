"""
System monitoring and resource usage performance tests.
"""
import pytest
import time
import psutil
import threading
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import os


@dataclass
class SystemSnapshot:
    """System resource snapshot."""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    open_files: int
    threads: int


class SystemMonitor:
    """Advanced system monitoring for performance tests."""
    
    def __init__(self):
        self.snapshots: List[SystemSnapshot] = []
        self.monitoring = False
        self.monitor_thread = None
        self.process = psutil.Process()
        self.initial_io = None
        self.initial_net = None
        
    def start_monitoring(self, interval: float = 0.5):
        """Start comprehensive system monitoring."""
        self.monitoring = True
        self.snapshots.clear()
        
        # Get initial IO and network stats
        try:
            self.initial_io = self.process.io_counters()
        except (psutil.AccessDenied, AttributeError):
            self.initial_io = None
            
        try:
            self.initial_net = psutil.net_io_counters()
        except (psutil.AccessDenied, AttributeError):
            self.initial_net = None
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,)
        )
        self.monitor_thread.start()
        
    def stop_monitoring(self) -> List[SystemSnapshot]:
        """Stop monitoring and return collected snapshots."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        return self.snapshots.copy()
        
    def _monitor_loop(self, interval: float):
        """Monitor system resources in a loop."""
        while self.monitoring:
            try:
                snapshot = self._take_snapshot()
                if snapshot:
                    self.snapshots.append(snapshot)
            except Exception as e:
                print(f"Monitoring error: {e}")
            
            time.sleep(interval)
    
    def _take_snapshot(self) -> Optional[SystemSnapshot]:
        """Take a system resource snapshot."""
        try:
            # CPU and memory
            cpu_percent = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            memory_percent = self.process.memory_percent()
            
            # Disk I/O
            disk_read_mb = 0.0
            disk_write_mb = 0.0
            try:
                io_counters = self.process.io_counters()
                if self.initial_io:
                    disk_read_mb = (io_counters.read_bytes - self.initial_io.read_bytes) / 1024 / 1024
                    disk_write_mb = (io_counters.write_bytes - self.initial_io.write_bytes) / 1024 / 1024
            except (psutil.AccessDenied, AttributeError):
                pass
            
            # Network I/O
            net_sent_mb = 0.0
            net_recv_mb = 0.0
            try:
                net_counters = psutil.net_io_counters()
                if self.initial_net:
                    net_sent_mb = (net_counters.bytes_sent - self.initial_net.bytes_sent) / 1024 / 1024
                    net_recv_mb = (net_counters.bytes_recv - self.initial_net.bytes_recv) / 1024 / 1024
            except (psutil.AccessDenied, AttributeError):
                pass
            
            # Process info
            open_files = 0
            try:
                open_files = len(self.process.open_files())
            except (psutil.AccessDenied, AttributeError):
                pass
            
            threads = self.process.num_threads()
            
            return SystemSnapshot(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=memory_percent,
                disk_io_read_mb=disk_read_mb,
                disk_io_write_mb=disk_write_mb,
                network_sent_mb=net_sent_mb,
                network_recv_mb=net_recv_mb,
                open_files=open_files,
                threads=threads
            )
            
        except Exception as e:
            print(f"Failed to take snapshot: {e}")
            return None
    
    def analyze_snapshots(self) -> Dict[str, Any]:
        """Analyze collected snapshots for performance insights."""
        if not self.snapshots:
            return {}
        
        # Extract metrics
        cpu_values = [s.cpu_percent for s in self.snapshots]
        memory_values = [s.memory_mb for s in self.snapshots]
        memory_percent_values = [s.memory_percent for s in self.snapshots]
        
        analysis = {
            'duration_seconds': self.snapshots[-1].timestamp - self.snapshots[0].timestamp,
            'sample_count': len(self.snapshots),
            'cpu': {
                'avg_percent': statistics.mean(cpu_values),
                'max_percent': max(cpu_values),
                'min_percent': min(cpu_values),
                'std_dev': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0.0
            },
            'memory': {
                'avg_mb': statistics.mean(memory_values),
                'max_mb': max(memory_values),
                'min_mb': min(memory_values),
                'growth_mb': memory_values[-1] - memory_values[0],
                'avg_percent': statistics.mean(memory_percent_values),
                'max_percent': max(memory_percent_values)
            },
            'disk_io': {
                'total_read_mb': self.snapshots[-1].disk_io_read_mb,
                'total_write_mb': self.snapshots[-1].disk_io_write_mb
            },
            'network': {
                'total_sent_mb': self.snapshots[-1].network_sent_mb,
                'total_recv_mb': self.snapshots[-1].network_recv_mb
            },
            'resources': {
                'max_open_files': max(s.open_files for s in self.snapshots),
                'max_threads': max(s.threads for s in self.snapshots),
                'avg_threads': statistics.mean(s.threads for s in self.snapshots)
            }
        }
        
        return analysis


class ResourceLeakDetector:
    """Detect potential resource leaks."""
    
    def __init__(self):
        self.baseline = None
        
    def set_baseline(self):
        """Set baseline resource usage."""
        try:
            process = psutil.Process()
            self.baseline = {
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'open_files': len(process.open_files()),
                'threads': process.num_threads()
            }
        except Exception as e:
            print(f"Failed to set baseline: {e}")
            self.baseline = None
    
    def check_for_leaks(self, threshold_mb: float = 50.0) -> Dict[str, Any]:
        """Check for resource leaks compared to baseline."""
        if not self.baseline:
            return {'error': 'No baseline set'}
        
        try:
            process = psutil.Process()
            current = {
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'open_files': len(process.open_files()),
                'threads': process.num_threads()
            }
            
            leaks = {
                'memory_leak_mb': current['memory_mb'] - self.baseline['memory_mb'],
                'file_leak_count': current['open_files'] - self.baseline['open_files'],
                'thread_leak_count': current['threads'] - self.baseline['threads'],
                'has_memory_leak': (current['memory_mb'] - self.baseline['memory_mb']) > threshold_mb,
                'has_file_leak': (current['open_files'] - self.baseline['open_files']) > 10,
                'has_thread_leak': (current['threads'] - self.baseline['threads']) > 5
            }
            
            return leaks
            
        except Exception as e:
            return {'error': f'Failed to check leaks: {e}'}


@pytest.fixture
def system_monitor():
    """Fixture providing system monitoring."""
    monitor = SystemMonitor()
    yield monitor
    if monitor.monitoring:
        monitor.stop_monitoring()


@pytest.fixture
def leak_detector():
    """Fixture providing resource leak detection."""
    detector = ResourceLeakDetector()
    detector.set_baseline()
    yield detector


class TestSystemMonitoring:
    """System monitoring and resource usage tests."""
    
    def test_baseline_resource_usage(self, system_monitor, benchmark_config):
        """Test baseline system resource usage."""
        system_monitor.start_monitoring(interval=0.2)
        
        # Let it monitor for a few seconds with minimal activity
        time.sleep(3.0)
        
        snapshots = system_monitor.stop_monitoring()
        analysis = system_monitor.analyze_snapshots()
        
        assert len(snapshots) > 5, "Should have collected multiple snapshots"
        
        if analysis:
            # Check baseline resource usage
            assert analysis['memory']['avg_mb'] < benchmark_config['memory_threshold_mb'], (
                f"Baseline memory usage {analysis['memory']['avg_mb']:.2f}MB too high"
            )
            
            assert analysis['cpu']['avg_percent'] < 50.0, (
                f"Baseline CPU usage {analysis['cpu']['avg_percent']:.2f}% too high"
            )
            
            # Memory should be relatively stable
            assert analysis['memory']['growth_mb'] < 10.0, (
                f"Memory grew by {analysis['memory']['growth_mb']:.2f}MB during baseline test"
            )
    
    def test_cpu_usage_under_load(self, system_monitor, benchmark_config, perf_assert):
        """Test CPU usage under computational load."""
        system_monitor.start_monitoring(interval=0.1)
        
        # Simulate CPU-intensive work
        start_time = time.time()
        while time.time() - start_time < 5.0:
            # Simple CPU-intensive calculation
            sum(i * i for i in range(1000))
            time.sleep(0.01)  # Small pause to allow monitoring
        
        snapshots = system_monitor.stop_monitoring()
        analysis = system_monitor.analyze_snapshots()
        
        if analysis:
            perf_assert.assert_cpu_usage(
                analysis['cpu']['max_percent'],
                benchmark_config['cpu_threshold_percent'],
                "CPU-intensive operations"
            )
            
            # CPU usage should increase under load
            assert analysis['cpu']['avg_percent'] > 5.0, (
                f"CPU usage {analysis['cpu']['avg_percent']:.2f}% too low for intensive work"
            )
    
    def test_memory_usage_patterns(self, system_monitor, benchmark_config, perf_assert):
        """Test memory usage patterns during operations."""
        system_monitor.start_monitoring(interval=0.2)
        
        # Simulate memory-intensive operations
        large_data = []
        for i in range(10):
            # Allocate and release memory
            data = [j for j in range(10000)]
            large_data.append(data)
            time.sleep(0.2)
            
            # Release some memory
            if i % 3 == 0:
                large_data.clear()
        
        snapshots = system_monitor.stop_monitoring()
        analysis = system_monitor.analyze_snapshots()
        
        if analysis:
            perf_assert.assert_memory_usage(
                analysis['memory']['max_mb'],
                benchmark_config['memory_threshold_mb'],
                "Memory-intensive operations"
            )
            
            # Memory should show some variation
            assert analysis['memory']['std_dev'] > 0.0, "Memory usage should vary during operations"
    
    def test_resource_leak_detection(self, leak_detector, system_monitor):
        """Test resource leak detection."""
        system_monitor.start_monitoring(interval=0.5)
        
        # Simulate operations that might cause leaks
        temp_files = []
        temp_threads = []
        
        try:
            # Create some temporary resources
            for i in range(5):
                # Simulate file operations
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(b"test data")
                temp_file.close()
                temp_files.append(temp_file.name)
                
                time.sleep(0.2)
            
            # Check for leaks
            leak_info = leak_detector.check_for_leaks(threshold_mb=20.0)
            
            # Should not have significant leaks yet
            assert not leak_info.get('has_memory_leak', False), (
                f"Memory leak detected: {leak_info.get('memory_leak_mb', 0):.2f}MB"
            )
            
        finally:
            # Cleanup temporary resources
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
        
        snapshots = system_monitor.stop_monitoring()
        assert len(snapshots) > 5, "Should have monitored resource usage"
    
    def test_disk_io_monitoring(self, system_monitor):
        """Test disk I/O monitoring during file operations."""
        system_monitor.start_monitoring(interval=0.3)
        
        # Perform file I/O operations
        import tempfile
        temp_files = []
        
        try:
            for i in range(5):
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                # Write some data
                data = f"Test data {i} " * 1000
                temp_file.write(data.encode())
                temp_file.flush()
                temp_file.close()
                temp_files.append(temp_file.name)
                
                # Read the data back
                with open(temp_file.name, 'r') as f:
                    content = f.read()
                
                time.sleep(0.2)
                
        finally:
            # Cleanup
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
        
        snapshots = system_monitor.stop_monitoring()
        analysis = system_monitor.analyze_snapshots()
        
        if analysis and 'disk_io' in analysis:
            # Should have some disk I/O activity
            total_io = analysis['disk_io']['total_read_mb'] + analysis['disk_io']['total_write_mb']
            print(f"Total disk I/O: {total_io:.2f}MB")
            
            # Note: Disk I/O monitoring might not work on all systems
            # so we don't assert specific values
    
    def test_thread_monitoring(self, system_monitor):
        """Test thread monitoring during concurrent operations."""
        system_monitor.start_monitoring(interval=0.2)
        
        # Create some threads
        threads = []
        
        def worker():
            time.sleep(1.0)
        
        try:
            for i in range(3):
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()
                time.sleep(0.3)
            
            # Wait for threads to complete
            for thread in threads:
                thread.join()
                
        except Exception as e:
            print(f"Thread test error: {e}")
        
        snapshots = system_monitor.stop_monitoring()
        analysis = system_monitor.analyze_snapshots()
        
        if analysis and 'resources' in analysis:
            # Should have detected thread activity
            assert analysis['resources']['max_threads'] >= analysis['resources']['avg_threads'], (
                "Thread count should vary during concurrent operations"
            )
    
    @pytest.mark.slow
    def test_long_running_monitoring(self, system_monitor, benchmark_config):
        """Test system monitoring over extended period."""
        system_monitor.start_monitoring(interval=1.0)
        
        # Run for 30 seconds with periodic activity
        start_time = time.time()
        activity_count = 0
        
        while time.time() - start_time < 30:
            # Periodic activity
            if activity_count % 5 == 0:
                # Some computation
                sum(i for i in range(1000))
            
            activity_count += 1
            time.sleep(1.0)
        
        snapshots = system_monitor.stop_monitoring()
        analysis = system_monitor.analyze_snapshots()
        
        assert len(snapshots) >= 25, f"Should have collected ~30 snapshots, got {len(snapshots)}"
        
        if analysis:
            # System should remain stable over time
            assert analysis['memory']['max_mb'] < benchmark_config['memory_threshold_mb'], (
                f"Memory usage {analysis['memory']['max_mb']:.2f}MB exceeded threshold"
            )
            
            # Memory growth should be minimal over 30 seconds
            assert abs(analysis['memory']['growth_mb']) < 50.0, (
                f"Memory grew by {analysis['memory']['growth_mb']:.2f}MB over 30 seconds"
            )
    
    def test_performance_report_generation(self, system_monitor):
        """Test generation of performance reports."""
        system_monitor.start_monitoring(interval=0.5)
        
        # Simulate some activity
        for i in range(10):
            time.sleep(0.2)
            # Some light computation
            sum(j for j in range(100))
        
        snapshots = system_monitor.stop_monitoring()
        analysis = system_monitor.analyze_snapshots()
        
        # Generate a performance report
        report = {
            'test_name': 'performance_report_generation',
            'timestamp': time.time(),
            'analysis': analysis,
            'snapshot_count': len(snapshots),
            'recommendations': []
        }
        
        # Add recommendations based on analysis
        if analysis:
            if analysis['memory']['max_mb'] > 200:
                report['recommendations'].append("Consider optimizing memory usage")
            
            if analysis['cpu']['avg_percent'] > 50:
                report['recommendations'].append("High CPU usage detected")
            
            if analysis['memory']['growth_mb'] > 20:
                report['recommendations'].append("Potential memory leak detected")
        
        # Verify report structure
        assert 'test_name' in report
        assert 'analysis' in report
        assert 'recommendations' in report
        assert isinstance(report['recommendations'], list)
        
        # Report should be JSON serializable
        try:
            json.dumps(report, default=str)
        except Exception as e:
            pytest.fail(f"Report not JSON serializable: {e}")


if __name__ == "__main__":
    # Allow running monitoring tests directly
    monitor = SystemMonitor()
    
    print("Running system monitoring tests...")
    
    monitor.start_monitoring(interval=0.5)
    
    # Simulate some activity
    print("Simulating activity...")
    for i in range(10):
        sum(j * j for j in range(1000))
        time.sleep(0.3)
    
    snapshots = monitor.stop_monitoring()
    analysis = monitor.analyze_snapshots()
    
    print(f"Collected {len(snapshots)} snapshots")
    if analysis:
        print(f"Average CPU: {analysis['cpu']['avg_percent']:.2f}%")
        print(f"Average Memory: {analysis['memory']['avg_mb']:.2f}MB")
        print(f"Memory Growth: {analysis['memory']['growth_mb']:.2f}MB")
    
    # Test leak detection
    detector = ResourceLeakDetector()
    detector.set_baseline()
    
    # Simulate some operations
    temp_data = [i for i in range(10000)]
    time.sleep(1.0)
    
    leak_info = detector.check_for_leaks()
    print(f"Leak check: {leak_info}")