"""File locking utilities for safe concurrent file access."""

import fcntl
import json
import os
import time
from pathlib import Path
from typing import Any, List, Optional, Callable
from contextlib import contextmanager

from pr_agent.utils.logger import get_logger

logger = get_logger(__name__)


@contextmanager
def file_lock(file_path: Path, timeout: float = 5.0, mode: str = 'r+'):
    """Context manager for file locking with timeout.
    
    Uses fcntl (Unix) for file locking. The file remains open while the lock is held.
    
    Args:
        file_path: Path to the file to lock
        timeout: Maximum time to wait for lock in seconds (default: 5.0)
        mode: File mode for opening ('r', 'r+', 'w', 'a', etc.)
        
    Yields:
        File object that is locked
        
    Raises:
        TimeoutError: If lock cannot be acquired within timeout
        IOError: If file cannot be opened
    """
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Open file in the requested mode
    # Use 'r+' for read-write, create if doesn't exist
    if mode == 'r+' and not file_path.exists():
        mode = 'w+'  # Create file if it doesn't exist
    elif mode == 'r' and not file_path.exists():
        # For read mode, create empty file if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump([], f)
    
    # Open file (will be closed when context exits)
    f = None
    try:
        f = open(file_path, mode)
        start_time = time.time()
        
        # Try to acquire lock with timeout
        while True:
            try:
                # Try to acquire exclusive lock (non-blocking)
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                logger.debug("File lock acquired", file_path=str(file_path))
                break
            except (IOError, OSError):
                # Lock is held by another process
                if time.time() - start_time >= timeout:
                    logger.error(
                        "Failed to acquire file lock within timeout",
                        file_path=str(file_path),
                        timeout=timeout
                    )
                    if f:
                        f.close()
                    raise TimeoutError(
                        f"Could not acquire lock on {file_path} within {timeout} seconds"
                    )
                time.sleep(0.1)  # Wait 100ms before retrying
        
        try:
            yield f
        finally:
            # Release lock
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                logger.debug("File lock released", file_path=str(file_path))
            except (IOError, OSError) as e:
                logger.warning(
                    "Error releasing file lock",
                    file_path=str(file_path),
                    error=str(e)
                )
    finally:
        # Close file
        if f:
            f.close()


def safe_read_json(file_path: Path, default: Any = None) -> Any:
    """Safely read JSON file with file locking.
    
    Args:
        file_path: Path to JSON file
        default: Default value to return if file doesn't exist or is invalid
        
    Returns:
        Parsed JSON data or default value
    """
    if not file_path.exists():
        logger.debug("File does not exist, returning default", file_path=str(file_path))
        return default if default is not None else []
    
    try:
        with file_lock(file_path, mode='r') as f:
            try:
                data = json.load(f)
                logger.debug("Successfully read JSON file", file_path=str(file_path))
                return data
            except json.JSONDecodeError as e:
                logger.error(
                    "Invalid JSON in file",
                    file_path=str(file_path),
                    error=str(e)
                )
                return default if default is not None else []
    except (IOError, OSError, TimeoutError) as e:
        logger.error(
            "Failed to read JSON file",
            file_path=str(file_path),
            error=str(e)
        )
        return default if default is not None else []


def safe_write_json(
    file_path: Path,
    data: Any,
    max_items: Optional[int] = None,
    indent: int = 2
) -> bool:
    """Safely write JSON file with file locking.
    
    Args:
        file_path: Path to JSON file
        data: Data to write (will be JSON serialized)
        max_items: If data is a list and max_items is set, keep only last N items
        indent: JSON indentation level
        
    Returns:
        True if write was successful, False otherwise
    """
    try:
        # If data is a list and max_items is specified, truncate
        if isinstance(data, list) and max_items is not None:
            if len(data) > max_items:
                data = data[-max_items:]
                logger.debug(
                    "Truncated list to max_items",
                    file_path=str(file_path),
                    max_items=max_items,
                    original_length=len(data) + (len(data) - max_items)
                )
        
        # Write with lock
        with file_lock(file_path, mode='w') as f:
            json.dump(data, f, indent=indent, default=str)
            f.flush()  # Ensure data is written to disk
            os.fsync(f.fileno())  # Force write to disk
        
        logger.debug("Successfully wrote JSON file", file_path=str(file_path))
        return True
    except (IOError, OSError, TimeoutError) as e:
        logger.error(
            "Failed to write JSON file",
            file_path=str(file_path),
            error=str(e)
        )
        return False


def safe_append_json(
    file_path: Path,
    new_item: Any,
    max_items: Optional[int] = None
) -> bool:
    """Safely append item to JSON list file with file locking.
    
    This function reads the existing file, appends the new item, and writes back.
    All operations are done with file locking to prevent race conditions.
    
    Args:
        file_path: Path to JSON file (should contain a list)
        new_item: Item to append to the list
        max_items: Maximum number of items to keep (keeps last N items)
        
    Returns:
        True if append was successful, False otherwise
    """
    try:
        # Read existing data
        existing_data = safe_read_json(file_path, default=[])
        
        # Ensure it's a list
        if not isinstance(existing_data, list):
            logger.warning(
                "File does not contain a list, creating new list",
                file_path=str(file_path)
            )
            existing_data = []
        
        # Append new item
        existing_data.append(new_item)
        
        # Write back with max_items limit
        return safe_write_json(file_path, existing_data, max_items=max_items)
    except Exception as e:
        logger.exception(
            "Failed to append to JSON file",
            file_path=str(file_path),
            error=str(e)
        )
        return False

