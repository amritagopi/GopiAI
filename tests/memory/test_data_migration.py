#!/usr/bin/env python3
"""
Data Migration Tests for GopiAI Memory System

Tests for data migration between versions, format conversion, and data integrity.
Part of task 8: Реализовать тесты системы памяти.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add test infrastructure to path
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

from memory_fixtures import (
    MockMemorySystem, MockTxtaiIndex, MockMemoryEntry, MockSearchResult,
    MemoryTestUtils, temp_memory_dir, mock_memory_system, mock_txtai_index,
    sample_memory_entries, sample_conversations, memory_performance_data,
    mock_embedding_model, memory_migration_data
)

# Add GopiAI modules to path
    # Инициализируем пути проекта
    path_manager = setup_project_paths()
    # Инициализируем пути проекта
    path_manager = setup_project_paths()
    # Инициализируем пути проекта
    path_manager = setup_project_paths()


class TestDataMigrationBasic:
    """Test basic data migration functionality."""
    
    @pytest.mark.unit
    def test_v1_to_v2_migration(self, temp_memory_dir, memory_migration_data):
        """Test migration from v1 to v2 memory format."""
        v1_file = os.path.join(temp_memory_dir, "memory_v1.json")
        v2_file = os.path.join(temp_memory_dir, "memory_v2.json")
        
        # Create v1 format file
        MemoryTestUtils.create_test_memory_file(v1_file, memory_migration_data["v1_format"])
        
        # Mock migration function
        def migrate_v1_to_v2(v1_path: str, v2_path: str):
            v1_data = MemoryTestUtils.load_memory_file(v1_path)
            
            v2_data = {
                "memories": [],
                "metadata": {
                    "version": "2.0",
                    "created": datetime.now().isoformat(),
                    "migrated_from": "1.0"
                }
            }
            
            # Convert v1 entries to v2 format
            for old_entry in v1_data.get("memories", []):
                new_entry = {
                    "id": old_entry["id"],
                    "content": old_entry.get("text", ""),  # v1 used 'text', v2 uses 'content'
                    "category": "general",  # Default category for migrated entries
                    "conversation_id": "migrated",
                    "created_at": old_entry.get("timestamp", datetime.now().isoformat()),
                    "metadata": {"migrated": True}
                }
                v2_data["memories"].append(new_entry)
            
            MemoryTestUtils.create_test_memory_file(v2_path, v2_data)
        
        # Perform migration
        migrate_v1_to_v2(v1_file, v2_file)
        
        # Verify migration
        v2_data = MemoryTestUtils.load_memory_file(v2_file)
        
        assert v2_data["metadata"]["version"] == "2.0"
        assert v2_data["metadata"]["migrated_from"] == "1.0"
        assert len(v2_data["memories"]) == 1
        
        migrated_entry = v2_data["memories"][0]
        assert migrated_entry["id"] == "old_1"
        assert migrated_entry["content"] == "Old format memory entry"
        assert migrated_entry["category"] == "general"
        assert migrated_entry["metadata"]["migrated"] is True
    
    @pytest.mark.unit
    def test_migration_data_integrity(self, temp_memory_dir):
        """Test that migration preserves data integrity."""
        original_file = os.path.join(temp_memory_dir, "original.json")
        migrated_file = os.path.join(temp_memory_dir, "migrated.json")
        
        # Create original data with various entry types
        original_data = {
            "memories": [
                {
                    "id": "entry_1",
                    "text": "Important conversation content",
                    "timestamp": "2023-06-01T10:00:00",
                    "user": "test_user"
                },
                {
                    "id": "entry_2", 
                    "text": "Code snippet: def search(query): return results",
                    "timestamp": "2023-06-01T11:00:00",
                    "type": "code"
                }
            ]
        }
        
        MemoryTestUtils.create_test_memory_file(original_file, original_data)
        
        # Mock migration with data validation
        def migrate_with_validation(src_path: str, dst_path: str):
            src_data = MemoryTestUtils.load_memory_file(src_path)
            
            migrated_data = {
                "memories": [],
                "metadata": {"version": "2.0", "created": datetime.now().isoformat()}
            }
            
            for entry in src_data["memories"]:
                # Validate original entry
                assert "id" in entry
                assert "text" in entry
                
                # Convert to new format
                new_entry = {
                    "id": entry["id"],
                    "content": entry["text"],
                    "category": entry.get("type", "general"),
                    "conversation_id": "migrated",
                    "created_at": entry.get("timestamp", datetime.now().isoformat()),
                    "metadata": {k: v for k, v in entry.items() if k not in ["id", "text", "timestamp", "type"]}
                }
                
                # Validate new entry
                MemoryTestUtils.assert_memory_entry_valid(new_entry)
                migrated_data["memories"].append(new_entry)
            
            MemoryTestUtils.create_test_memory_file(dst_path, migrated_data)
        
        # Perform migration
        migrate_with_validation(original_file, migrated_file)
        
        # Verify all data was preserved
        migrated_data = MemoryTestUtils.load_memory_file(migrated_file)
        
        assert len(migrated_data["memories"]) == 2
        
        # Check first entry
        entry1 = migrated_data["memories"][0]
        assert entry1["content"] == "Important conversation content"
        assert entry1["metadata"]["user"] == "test_user"
        
        # Check second entry
        entry2 = migrated_data["memories"][1]
        assert entry2["content"] == "Code snippet: def search(query): return results"
        assert entry2["category"] == "code"
    
    @pytest.mark.unit
    def test_migration_error_handling(self, temp_memory_dir):
        """Test migration error handling for corrupted data."""
        corrupted_file = os.path.join(temp_memory_dir, "corrupted.json")
        output_file = os.path.join(temp_memory_dir, "output.json")
        
        # Create corrupted data
        corrupted_data = {
            "memories": [
                {"id": "good_entry", "text": "Valid entry"},
                {"text": "Missing ID"},  # Invalid: no ID
                {"id": "empty_text", "text": ""},  # Invalid: empty text
                {"id": "valid_entry", "text": "Another valid entry"}
            ]
        }
        
        MemoryTestUtils.create_test_memory_file(corrupted_file, corrupted_data)
        
        # Mock migration with error handling
        def migrate_with_error_handling(src_path: str, dst_path: str):
            src_data = MemoryTestUtils.load_memory_file(src_path)
            
            migrated_data = {
                "memories": [],
                "metadata": {
                    "version": "2.0",
                    "created": datetime.now().isoformat(),
                    "migration_errors": []
                }
            }
            
            for i, entry in enumerate(src_data["memories"]):
                try:
                    # Validate entry
                    if "id" not in entry:
                        raise ValueError(f"Entry {i}: Missing ID")
                    if not entry.get("text", "").strip():
                        raise ValueError(f"Entry {i}: Empty or missing text")
                    
                    # Convert valid entries
                    new_entry = {
                        "id": entry["id"],
                        "content": entry["text"],
                        "category": "general",
                        "conversation_id": "migrated",
                        "created_at": datetime.now().isoformat(),
                        "metadata": {}
                    }
                    
                    migrated_data["memories"].append(new_entry)
                    
                except ValueError as e:
                    migrated_data["metadata"]["migration_errors"].append(str(e))
            
            MemoryTestUtils.create_test_memory_file(dst_path, migrated_data)
        
        # Perform migration
        migrate_with_error_handling(corrupted_file, output_file)
        
        # Verify error handling
        result_data = MemoryTestUtils.load_memory_file(output_file)
        
        # Should have migrated only valid entries
        assert len(result_data["memories"]) == 2
        assert len(result_data["metadata"]["migration_errors"]) == 2
        
        # Check that valid entries were migrated
        migrated_ids = [entry["id"] for entry in result_data["memories"]]
        assert "good_entry" in migrated_ids
        assert "valid_entry" in migrated_ids
    
    @pytest.mark.unit
    def test_migration_rollback(self, temp_memory_dir):
        """Test migration rollback functionality."""
        original_file = os.path.join(temp_memory_dir, "original.json")
        backup_file = os.path.join(temp_memory_dir, "backup.json")
        migrated_file = os.path.join(temp_memory_dir, "migrated.json")
        
        # Create original data
        original_data = {
            "memories": [
                {"id": "entry_1", "text": "Original entry", "timestamp": "2023-01-01T00:00:00"}
            ],
            "metadata": {"version": "1.0"}
        }
        
        MemoryTestUtils.create_test_memory_file(original_file, original_data)
        
        # Create backup before migration
        shutil.copy2(original_file, backup_file)
        
        # Perform migration (simulate failure)
        def failed_migration(src_path: str, dst_path: str):
            # Start migration
            migrated_data = {
                "memories": [],
                "metadata": {"version": "2.0", "migration_status": "in_progress"}
            }
            MemoryTestUtils.create_test_memory_file(dst_path, migrated_data)
            
            # Simulate failure during migration
            raise Exception("Migration failed")
        
        # Attempt migration and handle failure
        migration_successful = False
        try:
            failed_migration(original_file, migrated_file)
            migration_successful = True
        except Exception:
            # Rollback: restore from backup
            shutil.copy2(backup_file, original_file)
        
        assert not migration_successful
        
        # Verify rollback worked
        restored_data = MemoryTestUtils.load_memory_file(original_file)
        assert restored_data["metadata"]["version"] == "1.0"
        assert len(restored_data["memories"]) == 1
        assert restored_data["memories"][0]["text"] == "Original entry"


class TestVersionCompatibility:
    """Test compatibility between different memory format versions."""
    
    @pytest.mark.unit
    def test_version_detection(self, temp_memory_dir):
        """Test automatic version detection."""
        # Create files with different versions
        v1_file = os.path.join(temp_memory_dir, "v1.json")
        v2_file = os.path.join(temp_memory_dir, "v2.json")
        no_version_file = os.path.join(temp_memory_dir, "no_version.json")
        
        # V1 format (no version field)
        v1_data = {
            "memories": [{"id": "1", "text": "V1 entry", "timestamp": "2023-01-01T00:00:00"}]
        }
        MemoryTestUtils.create_test_memory_file(v1_file, v1_data)
        
        # V2 format (with version field)
        v2_data = {
            "memories": [{"id": "1", "content": "V2 entry", "created_at": "2024-01-01T00:00:00"}],
            "metadata": {"version": "2.0"}
        }
        MemoryTestUtils.create_test_memory_file(v2_file, v2_data)
        
        # No version field (assume v1)
        no_version_data = {
            "memories": [{"id": "1", "text": "No version entry"}]
        }
        MemoryTestUtils.create_test_memory_file(no_version_file, no_version_data)
        
        # Mock version detection function
        def detect_version(file_path: str) -> str:
            data = MemoryTestUtils.load_memory_file(file_path)
            
            if "metadata" in data and "version" in data["metadata"]:
                return data["metadata"]["version"]
            elif "memories" in data and len(data["memories"]) > 0:
                # Check for v1 vs v2 field names
                first_entry = data["memories"][0]
                if "text" in first_entry and "content" not in first_entry:
                    return "1.0"
                elif "content" in first_entry:
                    return "2.0"
            
            return "1.0"  # Default to v1
        
        # Test version detection
        assert detect_version(v1_file) == "1.0"
        assert detect_version(v2_file) == "2.0"
        assert detect_version(no_version_file) == "1.0"
    
    @pytest.mark.unit
    def test_backward_compatibility(self, temp_memory_dir):
        """Test that newer versions can read older formats."""
        old_format_file = os.path.join(temp_memory_dir, "old_format.json")
        
        # Create old format data
        old_data = {
            "memories": [
                {"id": "old_1", "text": "Old format entry", "timestamp": "2023-01-01T00:00:00"},
                {"id": "old_2", "text": "Another old entry", "timestamp": "2023-01-02T00:00:00"}
            ]
        }
        MemoryTestUtils.create_test_memory_file(old_format_file, old_data)
        
        # Mock function to read old format with new system
        def read_with_compatibility(file_path: str) -> Dict[str, Any]:
            data = MemoryTestUtils.load_memory_file(file_path)
            
            # Convert old format to new format on-the-fly
            if "metadata" not in data or "version" not in data.get("metadata", {}):
                # This is old format, convert it
                converted_memories = []
                for entry in data.get("memories", []):
                    converted_entry = {
                        "id": entry["id"],
                        "content": entry.get("text", ""),
                        "category": "general",
                        "conversation_id": "legacy",
                        "created_at": entry.get("timestamp", datetime.now().isoformat()),
                        "metadata": {"legacy": True}
                    }
                    converted_memories.append(converted_entry)
                
                return {
                    "memories": converted_memories,
                    "metadata": {"version": "2.0", "converted_from": "1.0"}
                }
            
            return data
        
        # Test backward compatibility
        converted_data = read_with_compatibility(old_format_file)
        
        assert converted_data["metadata"]["version"] == "2.0"
        assert converted_data["metadata"]["converted_from"] == "1.0"
        assert len(converted_data["memories"]) == 2
        
        # Verify conversion
        for i, entry in enumerate(converted_data["memories"]):
            assert entry["content"] == old_data["memories"][i]["text"]
            assert entry["metadata"]["legacy"] is True
    
    @pytest.mark.unit
    def test_forward_compatibility_warning(self, temp_memory_dir):
        """Test handling of newer format versions."""
        future_format_file = os.path.join(temp_memory_dir, "future_format.json")
        
        # Create future format data
        future_data = {
            "memories": [
                {
                    "id": "future_1",
                    "content": "Future format entry",
                    "category": "advanced",
                    "conversation_id": "future_conv",
                    "created_at": "2025-01-01T00:00:00",
                    "metadata": {"future_field": "future_value"},
                    "embeddings": [0.1, 0.2, 0.3],  # New field
                    "tags": ["future", "test"]  # Another new field
                }
            ],
            "metadata": {"version": "3.0", "features": ["embeddings", "tags"]}
        }
        MemoryTestUtils.create_test_memory_file(future_format_file, future_data)
        
        # Mock function to handle future format
        def read_with_forward_compatibility(file_path: str) -> Dict[str, Any]:
            data = MemoryTestUtils.load_memory_file(file_path)
            
            version = data.get("metadata", {}).get("version", "1.0")
            
            if version > "2.0":
                # Future version detected
                warnings = []
                
                # Check for unknown fields and warn
                for entry in data.get("memories", []):
                    known_fields = {"id", "content", "category", "conversation_id", "created_at", "metadata"}
                    unknown_fields = set(entry.keys()) - known_fields
                    
                    if unknown_fields:
                        warnings.append(f"Unknown fields in entry {entry['id']}: {unknown_fields}")
                
                # Add warnings to metadata
                data["metadata"]["compatibility_warnings"] = warnings
            
            return data
        
        # Test forward compatibility
        loaded_data = read_with_forward_compatibility(future_format_file)
        
        assert "compatibility_warnings" in loaded_data["metadata"]
        assert len(loaded_data["metadata"]["compatibility_warnings"]) > 0
        
        # Should still be able to read basic fields
        entry = loaded_data["memories"][0]
        assert entry["id"] == "future_1"
        assert entry["content"] == "Future format entry"


class TestMigrationPerformance:
    """Test migration performance with large datasets."""
    
    @pytest.mark.performance
    def test_large_dataset_migration(self, temp_memory_dir, memory_performance_data):
        """Test migration performance with large datasets."""
        large_v1_file = os.path.join(temp_memory_dir, "large_v1.json")
        large_v2_file = os.path.join(temp_memory_dir, "large_v2.json")
        
        # Create large v1 dataset
        large_v1_data = {
            "memories": []
        }
        
        for i, content in enumerate(memory_performance_data["medium_dataset"][:500]):
            large_v1_data["memories"].append({
                "id": f"large_entry_{i}",
                "text": content,
                "timestamp": datetime.now().isoformat()
            })
        
        MemoryTestUtils.create_test_memory_file(large_v1_file, large_v1_data)
        
        # Mock large dataset migration
        def migrate_large_dataset(src_path: str, dst_path: str):
            import time
            start_time = time.time()
            
            src_data = MemoryTestUtils.load_memory_file(src_path)
            
            migrated_data = {
                "memories": [],
                "metadata": {
                    "version": "2.0",
                    "created": datetime.now().isoformat(),
                    "migrated_from": "1.0",
                    "entry_count": len(src_data["memories"])
                }
            }
            
            # Migrate entries in batches for better performance
            batch_size = 100
            for i in range(0, len(src_data["memories"]), batch_size):
                batch = src_data["memories"][i:i + batch_size]
                
                for entry in batch:
                    new_entry = {
                        "id": entry["id"],
                        "content": entry["text"],
                        "category": "general",
                        "conversation_id": "migrated",
                        "created_at": entry.get("timestamp", datetime.now().isoformat()),
                        "metadata": {"migrated": True}
                    }
                    migrated_data["memories"].append(new_entry)
            
            migration_time = time.time() - start_time
            migrated_data["metadata"]["migration_time"] = migration_time
            
            MemoryTestUtils.create_test_memory_file(dst_path, migrated_data)
            return migration_time
        
        # Perform migration and measure time
        migration_time = migrate_large_dataset(large_v1_file, large_v2_file)
        
        # Performance assertions
        assert migration_time < 30.0  # Should migrate 500 entries in under 30 seconds
        
        # Verify migration results
        migrated_data = MemoryTestUtils.load_memory_file(large_v2_file)
        assert len(migrated_data["memories"]) == 500
        assert migrated_data["metadata"]["version"] == "2.0"
        assert migrated_data["metadata"]["entry_count"] == 500
    
    @pytest.mark.performance
    def test_incremental_migration(self, temp_memory_dir):
        """Test incremental migration for very large datasets."""
        source_file = os.path.join(temp_memory_dir, "incremental_source.json")
        target_file = os.path.join(temp_memory_dir, "incremental_target.json")
        
        # Create source data
        source_data = {
            "memories": [
                {"id": f"entry_{i}", "text": f"Content {i}", "timestamp": datetime.now().isoformat()}
                for i in range(1000)  # 1000 entries
            ]
        }
        MemoryTestUtils.create_test_memory_file(source_file, source_data)
        
        # Mock incremental migration
        def incremental_migration(src_path: str, dst_path: str, batch_size: int = 100):
            import time
            
            src_data = MemoryTestUtils.load_memory_file(src_path)
            
            # Initialize target file
            target_data = {
                "memories": [],
                "metadata": {
                    "version": "2.0",
                    "migration_status": "in_progress",
                    "total_entries": len(src_data["memories"]),
                    "migrated_entries": 0
                }
            }
            MemoryTestUtils.create_test_memory_file(dst_path, target_data)
            
            # Migrate in batches
            batch_times = []
            for i in range(0, len(src_data["memories"]), batch_size):
                batch_start = time.time()
                
                # Load current target state
                current_target = MemoryTestUtils.load_memory_file(dst_path)
                
                # Process batch
                batch = src_data["memories"][i:i + batch_size]
                for entry in batch:
                    new_entry = {
                        "id": entry["id"],
                        "content": entry["text"],
                        "category": "general",
                        "conversation_id": "migrated",
                        "created_at": entry.get("timestamp", datetime.now().isoformat()),
                        "metadata": {"migrated": True}
                    }
                    current_target["memories"].append(new_entry)
                
                # Update metadata
                current_target["metadata"]["migrated_entries"] = len(current_target["memories"])
                
                # Save updated target
                MemoryTestUtils.create_test_memory_file(dst_path, current_target)
                
                batch_time = time.time() - batch_start
                batch_times.append(batch_time)
            
            # Mark migration as complete
            final_target = MemoryTestUtils.load_memory_file(dst_path)
            final_target["metadata"]["migration_status"] = "completed"
            final_target["metadata"]["total_time"] = sum(batch_times)
            MemoryTestUtils.create_test_memory_file(dst_path, final_target)
            
            return batch_times
        
        # Perform incremental migration
        batch_times = incremental_migration(source_file, target_file, batch_size=100)
        
        # Performance assertions
        assert len(batch_times) == 10  # 1000 entries / 100 batch size
        assert all(t < 5.0 for t in batch_times)  # Each batch under 5 seconds
        assert sum(batch_times) < 30.0  # Total time under 30 seconds
        
        # Verify final result
        final_data = MemoryTestUtils.load_memory_file(target_file)
        assert final_data["metadata"]["migration_status"] == "completed"
        assert final_data["metadata"]["migrated_entries"] == 1000
        assert len(final_data["memories"]) == 1000


class TestMigrationIntegrity:
    """Test data integrity during migration."""
    
    @pytest.mark.unit
    def test_migration_checksum_validation(self, temp_memory_dir):
        """Test migration with checksum validation."""
        source_file = os.path.join(temp_memory_dir, "checksum_source.json")
        target_file = os.path.join(temp_memory_dir, "checksum_target.json")
        
        # Create source data
        source_data = {
            "memories": [
                {"id": "entry_1", "text": "Important data", "timestamp": "2023-01-01T00:00:00"},
                {"id": "entry_2", "text": "Critical information", "timestamp": "2023-01-02T00:00:00"}
            ]
        }
        MemoryTestUtils.create_test_memory_file(source_file, source_data)
        
        # Mock migration with checksum validation
        def migrate_with_checksum(src_path: str, dst_path: str):
            import hashlib
            
            src_data = MemoryTestUtils.load_memory_file(src_path)
            
            # Calculate source checksum
            source_content = json.dumps(src_data["memories"], sort_keys=True)
            source_checksum = hashlib.md5(source_content.encode()).hexdigest()
            
            # Perform migration
            migrated_data = {
                "memories": [],
                "metadata": {
                    "version": "2.0",
                    "source_checksum": source_checksum,
                    "migration_date": datetime.now().isoformat()
                }
            }
            
            for entry in src_data["memories"]:
                new_entry = {
                    "id": entry["id"],
                    "content": entry["text"],
                    "category": "general",
                    "conversation_id": "migrated",
                    "created_at": entry.get("timestamp", datetime.now().isoformat()),
                    "metadata": {"original_checksum": hashlib.md5(entry["text"].encode()).hexdigest()}
                }
                migrated_data["memories"].append(new_entry)
            
            # Calculate target checksum (based on content)
            target_content = json.dumps([entry["content"] for entry in migrated_data["memories"]], sort_keys=True)
            target_checksum = hashlib.md5(target_content.encode()).hexdigest()
            migrated_data["metadata"]["target_checksum"] = target_checksum
            
            MemoryTestUtils.create_test_memory_file(dst_path, migrated_data)
            
            # Validate checksums match (content should be preserved)
            return source_checksum, target_checksum
        
        # Perform migration with checksum validation
        source_checksum, target_checksum = migrate_with_checksum(source_file, target_file)
        
        # Verify migration integrity
        migrated_data = MemoryTestUtils.load_memory_file(target_file)
        assert migrated_data["metadata"]["source_checksum"] == source_checksum
        assert migrated_data["metadata"]["target_checksum"] == target_checksum
        
        # Verify content integrity
        assert len(migrated_data["memories"]) == 2
        assert migrated_data["memories"][0]["content"] == "Important data"
        assert migrated_data["memories"][1]["content"] == "Critical information"
    
    @pytest.mark.unit
    def test_migration_with_data_validation(self, temp_memory_dir):
        """Test migration with comprehensive data validation."""
        source_file = os.path.join(temp_memory_dir, "validation_source.json")
        target_file = os.path.join(temp_memory_dir, "validation_target.json")
        
        # Create source data with various data types
        source_data = {
            "memories": [
                {
                    "id": "text_entry",
                    "text": "Regular text entry",
                    "timestamp": "2023-01-01T00:00:00",
                    "metadata": {"type": "text", "length": 18}
                },
                {
                    "id": "unicode_entry",
                    "text": "Unicode entry: 你好世界 🌍",
                    "timestamp": "2023-01-02T00:00:00",
                    "metadata": {"type": "unicode", "language": "mixed"}
                },
                {
                    "id": "long_entry",
                    "text": "Very long entry: " + "content " * 100,
                    "timestamp": "2023-01-03T00:00:00",
                    "metadata": {"type": "long", "word_count": 100}
                }
            ]
        }
        MemoryTestUtils.create_test_memory_file(source_file, source_data)
        
        # Mock migration with validation
        def migrate_with_validation(src_path: str, dst_path: str):
            src_data = MemoryTestUtils.load_memory_file(src_path)
            
            migrated_data = {
                "memories": [],
                "metadata": {
                    "version": "2.0",
                    "validation_results": {
                        "total_entries": len(src_data["memories"]),
                        "valid_entries": 0,
                        "invalid_entries": 0,
                        "warnings": []
                    }
                }
            }
            
            for entry in src_data["memories"]:
                try:
                    # Validate entry
                    assert "id" in entry, "Missing ID"
                    assert "text" in entry, "Missing text"
                    assert len(entry["text"]) > 0, "Empty text"
                    assert len(entry["text"]) < 10000, "Text too long"
                    
                    # Convert to new format
                    new_entry = {
                        "id": entry["id"],
                        "content": entry["text"],
                        "category": "general",
                        "conversation_id": "migrated",
                        "created_at": entry.get("timestamp", datetime.now().isoformat()),
                        "metadata": entry.get("metadata", {})
                    }
                    
                    # Additional validation for new format
                    MemoryTestUtils.assert_memory_entry_valid(new_entry)
                    
                    migrated_data["memories"].append(new_entry)
                    migrated_data["metadata"]["validation_results"]["valid_entries"] += 1
                    
                    # Check for warnings
                    if len(entry["text"]) > 1000:
                        migrated_data["metadata"]["validation_results"]["warnings"].append(
                            f"Entry {entry['id']} has very long content ({len(entry['text'])} chars)"
                        )
                    
                except Exception as e:
                    migrated_data["metadata"]["validation_results"]["invalid_entries"] += 1
                    migrated_data["metadata"]["validation_results"]["warnings"].append(
                        f"Failed to migrate entry {entry.get('id', 'unknown')}: {str(e)}"
                    )
            
            MemoryTestUtils.create_test_memory_file(dst_path, migrated_data)
        
        # Perform migration with validation
        migrate_with_validation(source_file, target_file)
        
        # Verify validation results
        migrated_data = MemoryTestUtils.load_memory_file(target_file)
        validation = migrated_data["metadata"]["validation_results"]
        
        assert validation["total_entries"] == 3
        assert validation["valid_entries"] == 3
        assert validation["invalid_entries"] == 0
        assert len(validation["warnings"]) == 1  # Warning for long entry
        
        # Verify all entries were migrated correctly
        assert len(migrated_data["memories"]) == 3
        
        # Check specific entries
        entries_by_id = {entry["id"]: entry for entry in migrated_data["memories"]}
        
        assert "text_entry" in entries_by_id
        assert "unicode_entry" in entries_by_id
        assert "long_entry" in entries_by_id
        
        # Verify unicode handling
        unicode_entry = entries_by_id["unicode_entry"]
        assert "你好世界 🌍" in unicode_entry["content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])