"""
UI performance tests for PySide6 application responsiveness.
"""
import pytest
import time
import statistics
from typing import Dict


try:
    from PySide6.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout
    from PySide6.QtCore import QTimer, QThread, Signal, QEventLoop
    from PySide6.QtTest import QTest
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


class UIPerformanceBenchmark:
    """UI performance benchmark utilities."""
    
    def __init__(self, app):
        self.app = app
        self.response_times = []
        
    def measure_widget_creation_time(self, widget_class, count: int = 10) -> Dict[str, float]:
        """Measure time to create widgets."""
        creation_times = []
        
        for _ in range(count):
            start_time = time.perf_counter()
            widget = widget_class()
            widget.show()
            end_time = time.perf_counter()
            
            creation_times.append((end_time - start_time) * 1000)
            widget.close()
            widget.deleteLater()
        
        return {
            'avg_creation_time_ms': statistics.mean(creation_times),
            'min_creation_time_ms': min(creation_times),
            'max_creation_time_ms': max(creation_times),
            'total_time_ms': sum(creation_times)
        }
    
    def measure_text_input_responsiveness(self, text_widget, text_length: int = 1000) -> Dict[str, float]:
        """Measure text input responsiveness."""
        test_text = "A" * text_length
        input_times = []
        
        # Measure character-by-character input
        for i in range(0, len(test_text), 100):  # Test every 100 characters
            chunk = test_text[i:i+100]
            
            start_time = time.perf_counter()
            text_widget.insertPlainText(chunk)
            self.app.processEvents()  # Process UI events
            end_time = time.perf_counter()
            
            input_times.append((end_time - start_time) * 1000)
        
        return {
            'avg_input_time_ms': statistics.mean(input_times),
            'max_input_time_ms': max(input_times),
            'total_input_time_ms': sum(input_times),
            'chars_per_second': text_length / (sum(input_times) / 1000) if input_times else 0
        }
    
    def measure_ui_update_frequency(self, widget, duration_seconds: int = 5) -> Dict[str, float]:
        """Measure UI update frequency and responsiveness."""
        update_count = 0
        update_times = []
        
        def update_ui():
            nonlocal update_count
            start_time = time.perf_counter()
            
            # Simulate UI update
            widget.update()
            self.app.processEvents()
            
            end_time = time.perf_counter()
            update_times.append((end_time - start_time) * 1000)
            update_count += 1
        
        # Create timer for regular updates
        timer = QTimer()
        timer.timeout.connect(update_ui)
        timer.start(100)  # Update every 100ms
        
        # Run for specified duration
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            self.app.processEvents()
            time.sleep(0.01)
        
        timer.stop()
        
        return {
            'total_updates': update_count,
            'updates_per_second': update_count / duration_seconds,
            'avg_update_time_ms': statistics.mean(update_times) if update_times else 0,
            'max_update_time_ms': max(update_times) if update_times else 0
        }
    
    def simulate_user_interaction_load(self, widget, interaction_count: int = 100) -> Dict[str, float]:
        """Simulate heavy user interaction load."""
        interaction_times = []
        
        for i in range(interaction_count):
            start_time = time.perf_counter()
            
            # Simulate various user interactions
            if hasattr(widget, 'mousePressEvent'):
                # Simulate mouse click
                QTest.mouseClick(widget, 1)  # Left click
            
            if hasattr(widget, 'keyPressEvent'):
                # Simulate key press
                QTest.keyClick(widget, ord('A'))
            
            # Process events
            self.app.processEvents()
            
            end_time = time.perf_counter()
            interaction_times.append((end_time - start_time) * 1000)
        
        return {
            'avg_interaction_time_ms': statistics.mean(interaction_times),
            'max_interaction_time_ms': max(interaction_times),
            'interactions_per_second': len(interaction_times) / (sum(interaction_times) / 1000) if interaction_times else 0
        }


@pytest.fixture
def ui_benchmark(qtbot):
    """Fixture providing UI performance benchmark utilities."""
    if not PYSIDE6_AVAILABLE:
        pytest.skip("PySide6 not available for UI performance tests")
    
    app = QApplication.instance()
    return UIPerformanceBenchmark(app)


class MockMainWindow(QWidget):
    """Mock main window for testing."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Window")
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)


class MockChatWidget(QWidget):
    """Mock chat widget for testing."""
    
    def __init__(self):
        super().__init__()
        self.messages = []
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        self.setLayout(layout)
    
    def add_message(self, message: str):
        """Add a message to the chat."""
        self.messages.append(message)
        self.chat_display.append(message)


@pytest.mark.skipif(not PYSIDE6_AVAILABLE, reason="PySide6 not available")
class TestUIPerformance:
    """UI performance tests."""
    
    def test_widget_creation_performance(self, ui_benchmark, benchmark_config, perf_assert):
        """Test widget creation performance."""
        metrics = ui_benchmark.measure_widget_creation_time(MockMainWindow, count=5)
        
        perf_assert.assert_response_time(
            metrics['avg_creation_time_ms'],
            benchmark_config['ui_response_threshold_ms'],
            "Widget creation"
        )
        
        assert metrics['max_creation_time_ms'] < 500.0, (
            f"Widget creation took {metrics['max_creation_time_ms']:.2f}ms max"
        )
    
    def test_text_input_responsiveness(self, ui_benchmark, qtbot, benchmark_config, perf_assert):
        """Test text input responsiveness."""
        window = MockMainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Test with different text lengths
        test_cases = [
            ("small", 100),
            ("medium", 1000),
            ("large", 5000)
        ]
        
        for size, length in test_cases:
            window.text_edit.clear()
            metrics = ui_benchmark.measure_text_input_responsiveness(
                window.text_edit, 
                text_length=length
            )
            
            # Adjust threshold based on text size
            threshold_multiplier = {"small": 1.0, "medium": 2.0, "large": 5.0}[size]
            adjusted_threshold = benchmark_config['ui_response_threshold_ms'] * threshold_multiplier
            
            perf_assert.assert_response_time(
                metrics['avg_input_time_ms'],
                adjusted_threshold,
                f"Text input ({size})"
            )
            
            assert metrics['chars_per_second'] > 100.0, (
                f"Text input rate {metrics['chars_per_second']:.2f} chars/sec too slow for {size} text"
            )
    
    def test_ui_update_frequency(self, ui_benchmark, qtbot, benchmark_config):
        """Test UI update frequency and responsiveness."""
        window = MockMainWindow()
        qtbot.addWidget(window)
        window.show()
        
        metrics = ui_benchmark.measure_ui_update_frequency(window, duration_seconds=3)
        
        assert metrics['updates_per_second'] >= 5.0, (
            f"UI update frequency {metrics['updates_per_second']:.2f} updates/sec too low"
        )
        
        assert metrics['avg_update_time_ms'] < 50.0, (
            f"UI updates took {metrics['avg_update_time_ms']:.2f}ms on average"
        )
        
        assert metrics['max_update_time_ms'] < 200.0, (
            f"Maximum UI update time {metrics['max_update_time_ms']:.2f}ms too high"
        )
    
    def test_chat_widget_message_performance(self, ui_benchmark, qtbot, benchmark_config, perf_assert):
        """Test chat widget performance with many messages."""
        chat_widget = MockChatWidget()
        qtbot.addWidget(chat_widget)
        chat_widget.show()
        
        # Add messages and measure performance
        message_count = 50
        start_time = time.perf_counter()
        
        for i in range(message_count):
            message = f"Test message {i}: This is a test message for performance testing."
            chat_widget.add_message(message)
            
            # Process events every 10 messages
            if i % 10 == 0:
                QApplication.processEvents()
        
        end_time = time.perf_counter()
        total_time_ms = (end_time - start_time) * 1000
        
        perf_assert.assert_response_time(
            total_time_ms,
            5000.0,  # 5 seconds for 50 messages
            "Chat message addition"
        )
        
        messages_per_second = message_count / (total_time_ms / 1000)
        assert messages_per_second > 10.0, (
            f"Message addition rate {messages_per_second:.2f} messages/sec too slow"
        )
    
    def test_user_interaction_responsiveness(self, ui_benchmark, qtbot, benchmark_config, perf_assert):
        """Test responsiveness under heavy user interaction."""
        window = MockMainWindow()
        qtbot.addWidget(window)
        window.show()
        
        metrics = ui_benchmark.simulate_user_interaction_load(window, interaction_count=20)
        
        perf_assert.assert_response_time(
            metrics['avg_interaction_time_ms'],
            benchmark_config['ui_response_threshold_ms'],
            "User interactions"
        )
        
        assert metrics['interactions_per_second'] > 10.0, (
            f"Interaction rate {metrics['interactions_per_second']:.2f} interactions/sec too slow"
        )
        
        assert metrics['max_interaction_time_ms'] < 500.0, (
            f"Maximum interaction time {metrics['max_interaction_time_ms']:.2f}ms too high"
        )
    
    def test_memory_usage_during_ui_operations(self, ui_benchmark, qtbot, performance_monitor, 
                                             benchmark_config, perf_assert):
        """Test memory usage during UI operations."""
        performance_monitor.start_monitoring(interval=0.2)
        
        # Create and use UI components
        window = MockMainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Perform various UI operations
        for i in range(20):
            window.text_edit.append(f"Test line {i}")
            QApplication.processEvents()
            time.sleep(0.1)
        
        # Create additional widgets
        chat_widgets = []
        for i in range(5):
            chat = MockChatWidget()
            qtbot.addWidget(chat)
            chat.show()
            chat.add_message(f"Test message in widget {i}")
            chat_widgets.append(chat)
            QApplication.processEvents()
        
        metrics = performance_monitor.stop_monitoring()
        
        if metrics:
            max_memory = max(m.memory_mb for m in metrics)
            avg_cpu = statistics.mean(m.cpu_percent for m in metrics)
            
            perf_assert.assert_memory_usage(
                max_memory,
                benchmark_config['memory_threshold_mb'],
                "UI operations"
            )
            
            perf_assert.assert_cpu_usage(
                avg_cpu,
                benchmark_config['cpu_threshold_percent'],
                "UI operations"
            )
    
    @pytest.mark.slow
    def test_ui_stress_test(self, ui_benchmark, qtbot, performance_monitor, benchmark_config):
        """Stress test UI with sustained operations."""
        performance_monitor.start_monitoring(interval=1.0)
        
        window = MockMainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Run sustained UI operations for 30 seconds
        start_time = time.time()
        operation_count = 0
        
        while time.time() - start_time < 30:
            try:
                # Add text
                window.text_edit.append(f"Stress test line {operation_count}")
                
                # Simulate user interaction
                if operation_count % 5 == 0:
                    QTest.keyClick(window.text_edit, ord('A'))
                
                QApplication.processEvents()
                operation_count += 1
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"UI operation failed: {e}")
        
        system_metrics = performance_monitor.stop_monitoring()
        
        # Verify UI remained responsive
        if system_metrics:
            avg_memory = statistics.mean(m.memory_mb for m in system_metrics)
            max_memory = max(m.memory_mb for m in system_metrics)
            
            assert max_memory < benchmark_config['memory_threshold_mb'], (
                f"Memory usage {max_memory:.2f}MB exceeded threshold during UI stress test"
            )
            
            # Check for memory leaks in UI
            if len(system_metrics) > 10:
                early_avg = statistics.mean(m.memory_mb for m in system_metrics[:5])
                late_avg = statistics.mean(m.memory_mb for m in system_metrics[-5:])
                memory_growth = late_avg - early_avg
                
                assert memory_growth < 100.0, (
                    f"UI memory grew by {memory_growth:.2f}MB during stress test"
                )
        
        assert operation_count > 100, f"Only completed {operation_count} operations in 30 seconds"
    
    def test_theme_switching_performance(self, ui_benchmark, qtbot, benchmark_config, perf_assert):
        """Test performance of theme switching."""
        window = MockMainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Simulate theme switching
        theme_switch_times = []
        themes = ["light", "dark", "blue", "green"]
        
        for theme in themes:
            start_time = time.perf_counter()
            
            # Simulate theme change by updating stylesheet
            if theme == "dark":
                window.setStyleSheet("background-color: #2b2b2b; color: white;")
            elif theme == "blue":
                window.setStyleSheet("background-color: #1e3a8a; color: white;")
            elif theme == "green":
                window.setStyleSheet("background-color: #166534; color: white;")
            else:
                window.setStyleSheet("")  # Default theme
            
            QApplication.processEvents()
            
            end_time = time.perf_counter()
            theme_switch_times.append((end_time - start_time) * 1000)
        
        avg_switch_time = statistics.mean(theme_switch_times)
        max_switch_time = max(theme_switch_times)
        
        perf_assert.assert_response_time(
            avg_switch_time,
            200.0,  # Theme switching should be fast
            "Theme switching"
        )
        
        assert max_switch_time < 500.0, (
            f"Maximum theme switch time {max_switch_time:.2f}ms too high"
        )


if __name__ == "__main__":
    # Allow running UI benchmarks directly (requires display)
    if PYSIDE6_AVAILABLE:
        app = QApplication([])
        benchmark = UIPerformanceBenchmark(app)
        
        print("Running UI performance benchmarks...")
        
        # Widget creation benchmark
        creation_metrics = benchmark.measure_widget_creation_time(MockMainWindow, count=3)
        print(f"Widget creation: {creation_metrics['avg_creation_time_ms']:.2f}ms avg")
        
        # Text input benchmark
        window = MockMainWindow()
        window.show()
        input_metrics = benchmark.measure_text_input_responsiveness(window.text_edit, 500)
        print(f"Text input: {input_metrics['avg_input_time_ms']:.2f}ms avg, "
              f"{input_metrics['chars_per_second']:.2f} chars/sec")
        
        window.close()
        app.quit()
    else:
        print("PySide6 not available for UI benchmarks")