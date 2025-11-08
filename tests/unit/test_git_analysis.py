#!/usr/bin/env python3
"""
Unit tests for git analysis tools.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from pr_agent.tools.git_analysis import register_git_analysis_tools
from mcp.server.fastmcp import FastMCP


@pytest.fixture
def mcp_server():
    """Create an MCP server instance for testing."""
    mcp = FastMCP("test")
    register_git_analysis_tools(mcp)
    return mcp


class TestAnalyzeFileChanges:
    """Test the analyze_file_changes tool."""
    
    @pytest.mark.asyncio
    async def test_analyze_with_diff(self, mcp_server):
        """Test analyzing changes with full diff included."""
        mock_result = MagicMock()
        mock_result.stdout = "M\tfile1.py\nA\tfile2.py\n"
        mock_result.stderr = ""
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = mock_result
            
            # Get the tool function from the server
            tool_func = None
            for tool in mcp_server._tools.values():
                if tool.name == "analyze_file_changes":
                    tool_func = tool.func
                    break
            
            if tool_func:
                result = await tool_func("main", include_diff=True)
                
                assert isinstance(result, str)
                data = json.loads(result)
                assert data["base_branch"] == "main"
                assert "files_changed" in data
                assert "statistics" in data
                assert "commits" in data
                assert "diff" in data
    
    @pytest.mark.asyncio
    async def test_analyze_without_diff(self, mcp_server):
        """Test analyzing changes without diff content."""
        mock_result = MagicMock()
        mock_result.stdout = "M\tfile1.py\n"
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = mock_result
            
            tool_func = None
            for tool in mcp_server._tools.values():
                if tool.name == "analyze_file_changes":
                    tool_func = tool.func
                    break
            
            if tool_func:
                result = await tool_func("main", include_diff=False)
                
                data = json.loads(result)
                assert "Diff not included" in data["diff"]
    
    @pytest.mark.asyncio
    async def test_analyze_git_error(self, mcp_server):
        """Test handling git command errors."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Git not found")
            
            tool_func = None
            for tool in mcp_server._tools.values():
                if tool.name == "analyze_file_changes":
                    tool_func = tool.func
                    break
            
            if tool_func:
                result = await tool_func("main", True)
                assert "Error:" in result

