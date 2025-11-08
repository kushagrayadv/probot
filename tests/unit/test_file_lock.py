"""Unit tests for file locking utilities."""

import json
import pytest
import tempfile
import threading
import time
import fcntl
from pathlib import Path

from pr_agent.utils.file_lock import (
    file_lock,
    safe_read_json,
    safe_write_json,
    safe_append_json
)


class TestFileLock:
    """Test file locking functionality."""
    
    def test_safe_read_json_nonexistent_file(self, tmp_path):
        """Test reading from non-existent file returns default."""
        file_path = tmp_path / "nonexistent.json"
        result = safe_read_json(file_path, default=[])
        assert result == []
    
    def test_safe_read_json_existing_file(self, tmp_path):
        """Test reading from existing file."""
        file_path = tmp_path / "test.json"
        data = [{"test": "data"}]
        with open(file_path, 'w') as f:
            json.dump(data, f)
        
        result = safe_read_json(file_path, default=[])
        assert result == data
    
    def test_safe_write_json(self, tmp_path):
        """Test writing JSON file."""
        file_path = tmp_path / "test.json"
        data = [{"test": "data"}]
        
        success = safe_write_json(file_path, data)
        assert success is True
        assert file_path.exists()
        
        with open(file_path, 'r') as f:
            result = json.load(f)
        assert result == data
    
    def test_safe_write_json_truncates_list(self, tmp_path):
        """Test that max_items truncates list correctly."""
        file_path = tmp_path / "test.json"
        data = list(range(150))  # 150 items
        
        success = safe_write_json(file_path, data, max_items=100)
        assert success is True
        
        result = safe_read_json(file_path, default=[])
        assert len(result) == 100
        assert result == list(range(50, 150))  # Last 100 items
    
    def test_safe_append_json(self, tmp_path):
        """Test appending to JSON file."""
        file_path = tmp_path / "test.json"
        
        # Append first item
        success = safe_append_json(file_path, {"id": 1})
        assert success is True
        
        # Append second item
        success = safe_append_json(file_path, {"id": 2})
        assert success is True
        
        result = safe_read_json(file_path, default=[])
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2
    
    def test_safe_append_json_max_items(self, tmp_path):
        """Test that append respects max_items."""
        file_path = tmp_path / "test.json"
        
        # Append 150 items
        for i in range(150):
            safe_append_json(file_path, {"id": i}, max_items=100)
        
        result = safe_read_json(file_path, default=[])
        assert len(result) == 100
        assert result[0]["id"] == 50  # First item should be 50
        assert result[-1]["id"] == 149  # Last item should be 149


class TestConcurrentAccess:
    """Test concurrent file access scenarios."""
    
    def test_concurrent_writes(self, tmp_path):
        """Test that concurrent writes don't corrupt the file."""
        file_path = tmp_path / "concurrent.json"
        num_threads = 10
        items_per_thread = 10
        errors = []
        
        def write_items(thread_id):
            """Write items from a thread."""
            try:
                for i in range(items_per_thread):
                    item = {"thread": thread_id, "item": i}
                    safe_append_json(file_path, item, max_items=200)
                    time.sleep(0.01)  # Small delay to increase chance of race condition
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads writing simultaneously
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=write_items, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Errors during concurrent writes: {errors}"
        
        # Verify file is valid JSON
        result = safe_read_json(file_path, default=[])
        assert isinstance(result, list)
        assert len(result) <= 200  # Should respect max_items
        
        # Verify all items are valid
        for item in result:
            assert isinstance(item, dict)
            assert "thread" in item
            assert "item" in item
    
    def test_concurrent_read_write(self, tmp_path):
        """Test that reads and writes can happen concurrently safely."""
        file_path = tmp_path / "readwrite.json"
        read_results = []
        errors = []
        
        def writer():
            """Write items."""
            try:
                for i in range(20):
                    safe_append_json(file_path, {"id": i}, max_items=50)
                    time.sleep(0.05)
            except Exception as e:
                errors.append(f"Writer error: {e}")
        
        def reader():
            """Read items."""
            try:
                for _ in range(10):
                    result = safe_read_json(file_path, default=[])
                    read_results.append(len(result))
                    time.sleep(0.1)
            except Exception as e:
                errors.append(f"Reader error: {e}")
        
        # Start writer and reader threads
        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)
        
        writer_thread.start()
        reader_thread.start()
        
        writer_thread.join()
        reader_thread.join()
        
        # Verify no errors
        assert len(errors) == 0, f"Errors during concurrent read/write: {errors}"
        
        # Verify all reads returned valid data
        assert all(isinstance(r, int) for r in read_results)
        
        # Final file should be valid
        final_result = safe_read_json(file_path, default=[])
        assert isinstance(final_result, list)
        assert len(final_result) <= 50
    
    def test_file_lock_timeout(self, tmp_path):
        """Test that file lock times out appropriately."""
        file_path = tmp_path / "timeout.json"
        
        # Create a file and hold a lock on it
        with open(file_path, 'w') as f:
            json.dump([], f)
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            
            # Try to acquire lock with short timeout (should fail)
            with pytest.raises(TimeoutError):
                with file_lock(file_path, timeout=0.1):
                    pass

