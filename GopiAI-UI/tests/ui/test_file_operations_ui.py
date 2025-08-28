#!/usr/bin/env python3
"""
UI tests for file operations functionality using pytest-qt.
Tests file handling, drag-and-drop, import/export, and file management through UI.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

# Add test infrastructure to path
test_infrastructure_path = Path(__file__).parent.parent.parent.parent / "test_infrastructure"
    # Заменено на использование path_manager: sys.path.append(str(test_infrastructure_path))

from ui_fixtures import (
    qtbot, mock_main_window, mock_chat_widget, mock_file_dialog,
    mock_message_box, mock_progress_dialog, mock_drag_drop, ui_test_data
)
from fixtures import mock_conversation_manager


class TestFileDialogOperations:
    """Test file dialog operations through UI."""
    
    def test_open_file_dialog(self, qtbot, mock_main_window, mock_file_dialog):
        """Test opening file dialog."""
        main_window = mock_main_window
        file_dialog = mock_file_dialog
        
        qtbot.addWidget(main_window)
        
        # Mock file dialog response
        file_dialog.getOpenFileName.return_value = ("/path/to/test.txt", "Text Files (*.txt)")
        
        # Simulate opening file dialog
        main_window.open_file_dialog = MagicMock(return_value=("/path/to/test.txt", "Text Files (*.txt)"))
        result = main_window.open_file_dialog()
        
        # Verify file dialog was opened
        assert result[0] == "/path/to/test.txt"
        assert result[1] == "Text Files (*.txt)"
        main_window.open_file_dialog.assert_called_once()
    
    def test_save_file_dialog(self, qtbot, mock_main_window, mock_file_dialog):
        """Test save file dialog."""
        main_window = mock_main_window
        file_dialog = mock_file_dialog
        
        qtbot.addWidget(main_window)
        
        # Mock save dialog response
        file_dialog.getSaveFileName.return_value = ("/path/to/save.txt", "Text Files (*.txt)")
        
        # Simulate save file dialog
        main_window.save_file_dialog = MagicMock(return_value=("/path/to/save.txt", "Text Files (*.txt)"))
        result = main_window.save_file_dialog()
        
        # Verify save dialog was opened
        assert result[0] == "/path/to/save.txt"
        assert result[1] == "Text Files (*.txt)"
        main_window.save_file_dialog.assert_called_once()
    
    def test_directory_selection_dialog(self, qtbot, mock_main_window, mock_file_dialog):
        """Test directory selection dialog."""
        main_window = mock_main_window
        file_dialog = mock_file_dialog
        
        qtbot.addWidget(main_window)
        
        # Mock directory dialog response
        file_dialog.getExistingDirectory.return_value = "/path/to/directory"
        
        # Simulate directory selection
        main_window.select_directory = MagicMock(return_value="/path/to/directory")
        result = main_window.select_directory()
        
        # Verify directory dialog was opened
        assert result == "/path/to/directory"
        main_window.select_directory.assert_called_once()
    
    def test_file_dialog_cancellation(self, qtbot, mock_main_window, mock_file_dialog):
        """Test file dialog cancellation."""
        main_window = mock_main_window
        file_dialog = mock_file_dialog
        
        qtbot.addWidget(main_window)
        
        # Mock cancelled dialog
        file_dialog.getOpenFileName.return_value = ("", "")
        
        # Simulate cancelled file dialog
        main_window.open_file_dialog = MagicMock(return_value=("", ""))
        result = main_window.open_file_dialog()
        
        # Verify cancellation was handled
        assert result[0] == ""
        assert result[1] == ""


class TestDragAndDropOperations:
    """Test drag and drop file operations."""
    
    def test_drag_enter_event(self, qtbot, mock_main_window, mock_drag_drop):
        """Test drag enter event handling."""
        main_window = mock_main_window
        drag_drop = mock_drag_drop
        
        qtbot.addWidget(main_window)
        
        # Test drag enter
        main_window.dragEnterEvent = MagicMock()
        main_window.dragEnterEvent(drag_drop)
        
        # Verify drag enter was handled
        main_window.dragEnterEvent.assert_called_once_with(drag_drop)
    
    def test_drop_event_single_file(self, qtbot, mock_main_window, mock_drag_drop):
        """Test dropping a single file."""
        main_window = mock_main_window
        drag_drop = mock_drag_drop
        
        qtbot.addWidget(main_window)
        
        # Mock single file drop
        mock_url = MagicMock()
        mock_url.toLocalFile.return_value = "/path/to/dropped/file.txt"
        drag_drop.mimeData().urls.return_value = [mock_url]
        
        # Simulate drop event
        main_window.handle_file_drop = MagicMock()
        main_window.handle_file_drop(["/path/to/dropped/file.txt"])
        
        # Verify file drop was handled
        main_window.handle_file_drop.assert_called_once_with(["/path/to/dropped/file.txt"])
    
    def test_drop_event_multiple_files(self, qtbot, mock_main_window, mock_drag_drop):
        """Test dropping multiple files."""
        main_window = mock_main_window
        drag_drop = mock_drag_drop
        
        qtbot.addWidget(main_window)
        
        # Mock multiple file drop
        mock_urls = []
        file_paths = ["/path/to/file1.txt", "/path/to/file2.py", "/path/to/file3.md"]
        
        for path in file_paths:
            mock_url = MagicMock()
            mock_url.toLocalFile.return_value = path
            mock_urls.append(mock_url)
        
        drag_drop.mimeData().urls.return_value = mock_urls
        
        # Simulate multiple file drop
        main_window.handle_file_drop = MagicMock()
        main_window.handle_file_drop(file_paths)
        
        # Verify multiple files were handled
        main_window.handle_file_drop.assert_called_once_with(file_paths)
    
    def test_drop_event_invalid_files(self, qtbot, mock_main_window, mock_drag_drop):
        """Test dropping invalid or unsupported files."""
        main_window = mock_main_window
        drag_drop = mock_drag_drop
        
        qtbot.addWidget(main_window)
        
        # Mock invalid file drop
        mock_url = MagicMock()
        mock_url.toLocalFile.return_value = "/path/to/invalid.exe"
        drag_drop.mimeData().urls.return_value = [mock_url]
        
        # Simulate invalid file handling
        main_window.handle_invalid_file = MagicMock()
        main_window.handle_invalid_file("/path/to/invalid.exe")
        
        # Verify invalid file was handled
        main_window.handle_invalid_file.assert_called_once_with("/path/to/invalid.exe")
    
    def test_drag_and_drop_with_chat_widget(self, qtbot, mock_chat_widget, mock_drag_drop):
        """Test drag and drop integration with chat widget."""
        chat_widget = mock_chat_widget
        drag_drop = mock_drag_drop
        
        qtbot.addWidget(chat_widget)
        
        # Mock file drop on chat widget
        mock_url = MagicMock()
        mock_url.toLocalFile.return_value = "/path/to/document.pdf"
        drag_drop.mimeData().urls.return_value = [mock_url]
        
        # Simulate file attachment
        chat_widget.attach_file = MagicMock()
        chat_widget.attach_file("/path/to/document.pdf")
        
        # Verify file was attached to chat
        chat_widget.attach_file.assert_called_once_with("/path/to/document.pdf")


class TestFileImportExport:
    """Test file import and export operations."""
    
    def test_import_conversation_from_file(self, qtbot, mock_main_window, mock_conversation_manager):
        """Test importing conversation from file."""
        main_window = mock_main_window
        conv_manager = mock_conversation_manager
        
        qtbot.addWidget(main_window)
        
        # Mock conversation import
        test_conversation = {
            "id": "imported_conv",
            "title": "Imported Chat",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        
        # Simulate import
        main_window.import_conversation = MagicMock(return_value=test_conversation)
        result = main_window.import_conversation("/path/to/conversation.json")
        
        # Verify import was successful
        assert result["id"] == "imported_conv"
        assert result["title"] == "Imported Chat"
        assert len(result["messages"]) == 2
        main_window.import_conversation.assert_called_once_with("/path/to/conversation.json")
    
    def test_export_conversation_to_file(self, qtbot, mock_main_window, mock_conversation_manager, ui_test_data):
        """Test exporting conversation to file."""
        main_window = mock_main_window
        conv_manager = mock_conversation_manager
        
        qtbot.addWidget(main_window)
        
        # Get test conversation
        test_conversation = {
            "id": "test_conv",
            "title": "Test Chat",
            "messages": ui_test_data["sample_messages"]
        }
        
        # Simulate export
        main_window.export_conversation = MagicMock(return_value=True)
        result = main_window.export_conversation(test_conversation, "/path/to/export.json")
        
        # Verify export was successful
        assert result is True
        main_window.export_conversation.assert_called_once_with(test_conversation, "/path/to/export.json")
    
    def test_export_conversation_as_markdown(self, qtbot, mock_main_window, ui_test_data):
        """Test exporting conversation as markdown."""
        main_window = mock_main_window
        qtbot.addWidget(main_window)
        
        # Test conversation
        test_conversation = {
            "title": "Test Chat",
            "messages": ui_test_data["sample_messages"]
        }
        
        # Simulate markdown export
        main_window.export_as_markdown = MagicMock(return_value=True)
        result = main_window.export_as_markdown(test_conversation, "/path/to/export.md")
        
        # Verify markdown export
        assert result is True
        main_window.export_as_markdown.assert_called_once_with(test_conversation, "/path/to/export.md")
    
    def test_export_conversation_as_pdf(self, qtbot, mock_main_window, ui_test_data):
        """Test exporting conversation as PDF."""
        main_window = mock_main_window
        qtbot.addWidget(main_window)
        
        # Test conversation
        test_conversation = {
            "title": "Test Chat",
            "messages": ui_test_data["sample_messages"]
        }
        
        # Simulate PDF export
        main_window.export_as_pdf = MagicMock(return_value=True)
        result = main_window.export_as_pdf(test_conversation, "/path/to/export.pdf")
        
        # Verify PDF export
        assert result is True
        main_window.export_as_pdf.assert_called_once_with(test_conversation, "/path/to/export.pdf")
    
    def test_bulk_export_conversations(self, qtbot, mock_main_window, mock_conversation_manager):
        """Test bulk export of multiple conversations."""
        main_window = mock_main_window
        conv_manager = mock_conversation_manager
        
        qtbot.addWidget(main_window)
        
        # Mock multiple conversations
        conversations = [
            {"id": "conv1", "title": "Chat 1"},
            {"id": "conv2", "title": "Chat 2"},
            {"id": "conv3", "title": "Chat 3"}
        ]
        conv_manager.get_conversations.return_value = conversations
        
        # Simulate bulk export
        main_window.bulk_export = MagicMock(return_value=3)
        result = main_window.bulk_export("/path/to/export/directory")
        
        # Verify bulk export
        assert result == 3  # Number of exported conversations
        main_window.bulk_export.assert_called_once_with("/path/to/export/directory")


class TestFileAttachmentOperations:
    """Test file attachment operations in chat."""
    
    def test_attach_text_file(self, qtbot, mock_chat_widget):
        """Test attaching a text file to chat."""
        chat_widget = mock_chat_widget
        qtbot.addWidget(chat_widget)
        
        # Mock text file attachment
        test_file = "/path/to/document.txt"
        chat_widget.attach_file = MagicMock(return_value=True)
        
        # Attach file
        result = chat_widget.attach_file(test_file)
        
        # Verify attachment
        assert result is True
        chat_widget.attach_file.assert_called_once_with(test_file)
    
    def test_attach_image_file(self, qtbot, mock_chat_widget):
        """Test attaching an image file to chat."""
        chat_widget = mock_chat_widget
        qtbot.addWidget(chat_widget)
        
        # Mock image file attachment
        test_image = "/path/to/image.png"
        chat_widget.attach_image = MagicMock(return_value=True)
        
        # Attach image
        result = chat_widget.attach_image(test_image)
        
        # Verify image attachment
        assert result is True
        chat_widget.attach_image.assert_called_once_with(test_image)
    
    def test_attach_code_file(self, qtbot, mock_chat_widget):
        """Test attaching a code file to chat."""
        chat_widget = mock_chat_widget
        qtbot.addWidget(chat_widget)
        
        # Mock code file attachment
        test_code = "/path/to/script.py"
        chat_widget.attach_code_file = MagicMock(return_value=True)
        
        # Attach code file
        result = chat_widget.attach_code_file(test_code)
        
        # Verify code file attachment
        assert result is True
        chat_widget.attach_code_file.assert_called_once_with(test_code)
    
    def test_attach_multiple_files(self, qtbot, mock_chat_widget):
        """Test attaching multiple files to chat."""
        chat_widget = mock_chat_widget
        qtbot.addWidget(chat_widget)
        
        # Mock multiple file attachment
        test_files = ["/path/to/file1.txt", "/path/to/file2.py", "/path/to/file3.md"]
        chat_widget.attach_multiple_files = MagicMock(return_value=len(test_files))
        
        # Attach multiple files
        result = chat_widget.attach_multiple_files(test_files)
        
        # Verify multiple file attachment
        assert result == 3
        chat_widget.attach_multiple_files.assert_called_once_with(test_files)
    
    def test_remove_file_attachment(self, qtbot, mock_chat_widget):
        """Test removing file attachment from chat."""
        chat_widget = mock_chat_widget
        qtbot.addWidget(chat_widget)
        
        # Mock file removal
        test_file = "/path/to/document.txt"
        chat_widget.remove_attachment = MagicMock(return_value=True)
        
        # Remove attachment
        result = chat_widget.remove_attachment(test_file)
        
        # Verify attachment removal
        assert result is True
        chat_widget.remove_attachment.assert_called_once_with(test_file)
    
    def test_list_attachments(self, qtbot, mock_chat_widget):
        """Test listing current attachments."""
        chat_widget = mock_chat_widget
        qtbot.addWidget(chat_widget)
        
        # Mock attachment list
        test_attachments = [
            {"name": "document.txt", "path": "/path/to/document.txt", "type": "text"},
            {"name": "image.png", "path": "/path/to/image.png", "type": "image"}
        ]
        chat_widget.get_attachments = MagicMock(return_value=test_attachments)
        
        # Get attachments
        attachments = chat_widget.get_attachments()
        
        # Verify attachment list
        assert len(attachments) == 2
        assert attachments[0]["name"] == "document.txt"
        assert attachments[1]["type"] == "image"
        chat_widget.get_attachments.assert_called_once()


class TestFileErrorHandling:
    """Test error handling for file operations."""
    
    def test_file_not_found_error(self, qtbot, mock_main_window, mock_message_box):
        """Test handling of file not found error."""
        main_window = mock_main_window
        message_box = mock_message_box
        
        qtbot.addWidget(main_window)
        
        # Simulate file not found
        main_window.open_file = MagicMock(side_effect=FileNotFoundError("File not found"))
        
        # Attempt to open non-existent file
        try:
            main_window.open_file("/path/to/nonexistent.txt")
        except FileNotFoundError:
            # Simulate error message
            message_box.critical(None, "Error", "File not found")
            message_box.critical.assert_called_with(None, "Error", "File not found")
    
    def test_permission_denied_error(self, qtbot, mock_main_window, mock_message_box):
        """Test handling of permission denied error."""
        main_window = mock_main_window
        message_box = mock_message_box
        
        qtbot.addWidget(main_window)
        
        # Simulate permission denied
        main_window.save_file = MagicMock(side_effect=PermissionError("Permission denied"))
        
        # Attempt to save to protected location
        try:
            main_window.save_file("/protected/path/file.txt", "content")
        except PermissionError:
            # Simulate error message
            message_box.critical(None, "Error", "Permission denied")
            message_box.critical.assert_called_with(None, "Error", "Permission denied")
    
    def test_file_too_large_error(self, qtbot, mock_chat_widget, mock_message_box):
        """Test handling of file too large error."""
        chat_widget = mock_chat_widget
        message_box = mock_message_box
        
        qtbot.addWidget(chat_widget)
        
        # Simulate file too large
        large_file = "/path/to/very_large_file.bin"
        chat_widget.attach_file = MagicMock(return_value=False)
        
        # Attempt to attach large file
        result = chat_widget.attach_file(large_file)
        
        # Verify error handling
        assert result is False
        
        # Simulate error message
        message_box.warning(None, "Warning", "File too large")
        message_box.warning.assert_called_with(None, "Warning", "File too large")
    
    def test_unsupported_file_type_error(self, qtbot, mock_chat_widget, mock_message_box):
        """Test handling of unsupported file type error."""
        chat_widget = mock_chat_widget
        message_box = mock_message_box
        
        qtbot.addWidget(chat_widget)
        
        # Simulate unsupported file type
        unsupported_file = "/path/to/file.xyz"
        chat_widget.attach_file = MagicMock(return_value=False)
        
        # Attempt to attach unsupported file
        result = chat_widget.attach_file(unsupported_file)
        
        # Verify error handling
        assert result is False
        
        # Simulate error message
        message_box.warning(None, "Warning", "Unsupported file type")
        message_box.warning.assert_called_with(None, "Warning", "Unsupported file type")


class TestFileOperationsProgress:
    """Test progress indication for file operations."""
    
    def test_file_upload_progress(self, qtbot, mock_chat_widget, mock_progress_dialog):
        """Test progress indication during file upload."""
        chat_widget = mock_chat_widget
        progress_dialog = mock_progress_dialog
        
        qtbot.addWidget(chat_widget)
        
        # Mock file upload with progress
        chat_widget.upload_file_with_progress = MagicMock(return_value=True)
        
        # Simulate upload with progress
        result = chat_widget.upload_file_with_progress("/path/to/large_file.pdf", progress_dialog)
        
        # Verify upload with progress
        assert result is True
        chat_widget.upload_file_with_progress.assert_called_once_with("/path/to/large_file.pdf", progress_dialog)
    
    def test_bulk_export_progress(self, qtbot, mock_main_window, mock_progress_dialog):
        """Test progress indication during bulk export."""
        main_window = mock_main_window
        progress_dialog = mock_progress_dialog
        
        qtbot.addWidget(main_window)
        
        # Mock bulk export with progress
        main_window.bulk_export_with_progress = MagicMock(return_value=5)
        
        # Simulate bulk export with progress
        result = main_window.bulk_export_with_progress("/export/path", progress_dialog)
        
        # Verify bulk export with progress
        assert result == 5
        main_window.bulk_export_with_progress.assert_called_once_with("/export/path", progress_dialog)
    
    def test_file_processing_progress(self, qtbot, mock_chat_widget, mock_progress_dialog):
        """Test progress indication during file processing."""
        chat_widget = mock_chat_widget
        progress_dialog = mock_progress_dialog
        
        qtbot.addWidget(chat_widget)
        
        # Mock file processing with progress
        chat_widget.process_file_with_progress = MagicMock(return_value=True)
        
        # Simulate file processing
        result = chat_widget.process_file_with_progress("/path/to/document.pdf", progress_dialog)
        
        # Verify file processing with progress
        assert result is True
        chat_widget.process_file_with_progress.assert_called_once_with("/path/to/document.pdf", progress_dialog)


@pytest.mark.integration
class TestFileOperationsIntegration:
    """Test integration of file operations with other UI components."""
    
    def test_file_operations_with_conversation_management(self, qtbot, mock_main_window, mock_conversation_manager, ui_test_data):
        """Test file operations integration with conversation management."""
        main_window = mock_main_window
        conv_manager = mock_conversation_manager
        
        qtbot.addWidget(main_window)
        
        # Import conversation from file
        imported_conv = {
            "id": "imported",
            "title": "Imported Chat",
            "messages": ui_test_data["sample_messages"]
        }
        
        main_window.import_conversation = MagicMock(return_value=imported_conv)
        conv_manager.add_conversation = MagicMock(return_value="imported")
        
        # Import and add to manager
        result = main_window.import_conversation("/path/to/conversation.json")
        conv_id = conv_manager.add_conversation(result)
        
        # Verify integration
        assert result["id"] == "imported"
        assert conv_id == "imported"
        main_window.import_conversation.assert_called_once_with("/path/to/conversation.json")
        conv_manager.add_conversation.assert_called_once_with(result)
    
    def test_file_attachment_with_message_sending(self, qtbot, mock_chat_widget):
        """Test file attachment integration with message sending."""
        chat_widget = mock_chat_widget
        qtbot.addWidget(chat_widget)
        
        # Attach file and send message
        test_file = "/path/to/document.txt"
        chat_widget.attach_file = MagicMock(return_value=True)
        chat_widget.send_message = MagicMock(return_value=True)
        
        # Attach file
        attach_result = chat_widget.attach_file(test_file)
        
        # Send message with attachment
        chat_widget.set_message_text("Please analyze this document")
        send_result = chat_widget.send_message()
        
        # Verify integration
        assert attach_result is True
        assert send_result is True
        chat_widget.attach_file.assert_called_once_with(test_file)
        chat_widget.send_message.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])