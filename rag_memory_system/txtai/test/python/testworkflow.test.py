import unittest
from unittest.mock import patch
import os
import tempfile
import io
from txtai.workflow import (
    Workflow,
    Task,
    ConsoleTask,
    ExportTask,
    ImageTask
)

from utils import Utils

class TestWorkflowUnit(unittest.TestCase):

    def test_task_creation(self):
        task = Task(lambda x: x * 2)
        self.assertTrue(callable(task.action))

    def test_workflow_execution(self):
        workflow = Workflow([Task(lambda x: x * 2)])
        result = list(workflow([1, 2, 3]))
        self.assertEqual(result, [2, 4, 6])

    def test_console_task(self):
        with patch('sys.stdout', new_callable=io.StringIO) as stdout:
            workflow = Workflow([ConsoleTask()])
            workflow([{"id": 1, "text": "test"}])
            self.assertIn("test", stdout.getvalue())

    def test_export_task(self):
        temp_file = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        temp_file_path = temp_file.name
        temp_file.close()

        workflow = Workflow([ExportTask(output=temp_file_path)])
        workflow([{"id": 1, "text": "test"}])
        self.assertTrue(os.path.exists(temp_file_path))
        os.remove(temp_file_path)

    def test_image_task(self):
        workflow = Workflow([ImageTask()])
        try:
            result = list(workflow([Utils.PATH + "/books.jpg"]))
            self.assertTrue(hasattr(result[0], 'size'))
        except FileNotFoundError:
            self.skipTest("Image file not found, skipping test.")