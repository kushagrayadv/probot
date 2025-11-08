"""Git utility functions."""

import os
import subprocess
from typing import Optional


def get_working_directory(mcp_context=None) -> str:
    """Get the working directory from MCP context or current directory.
    
    Args:
        mcp_context: Optional MCP context to get roots from
        
    Returns:
        Working directory path
    """
    if mcp_context:
        try:
            # This would need to be called with proper async context
            # For now, return current directory
            pass
        except Exception:
            pass
    
    return os.getcwd()


def run_git_command(cmd: list[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    """Run a git command and return the result.
    
    Args:
        cmd: Git command as list of strings
        cwd: Working directory for the command
        
    Returns:
        CompletedProcess result
    """
    return subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
        check=True,
        cwd=cwd or os.getcwd()
    )

