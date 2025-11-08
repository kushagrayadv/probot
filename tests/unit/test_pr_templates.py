#!/usr/bin/env python3
"""
Unit tests for PR template tools.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch
from pr_agent.tools.pr_templates import register_pr_template_tools
from pr_agent.config.settings import TEMPLATES_DIR
from mcp.server.fastmcp import FastMCP


@pytest.fixture
def mcp_server():
    """Create an MCP server instance for testing."""
    mcp = FastMCP("test")
    register_pr_template_tools(mcp)
    return mcp


class TestPRTemplates:
    """Test PR template management."""
    
    @pytest.mark.asyncio
    async def test_get_templates(self, mcp_server, tmp_path, monkeypatch):
        """Test getting available templates."""
        # Use temporary directory for templates
        monkeypatch.setattr('pr_agent.config.settings.TEMPLATES_DIR', tmp_path)
        
        # Create a test template
        test_template = tmp_path / "feature.md"
        test_template.write_text("## Feature\nTest content")
        
        tool_func = None
        for tool in mcp_server._tools.values():
            if tool.name == "get_pr_templates":
                tool_func = tool.func
                break
        
        if tool_func:
            result = await tool_func()
            
            templates = json.loads(result)
            assert len(templates) > 0
    
    @pytest.mark.asyncio
    async def test_suggest_bug_fix(self, mcp_server, tmp_path, monkeypatch):
        """Test suggesting bug fix template."""
        monkeypatch.setattr('pr_agent.config.settings.TEMPLATES_DIR', tmp_path)
        
        # Create test templates
        bug_template = tmp_path / "bug.md"
        bug_template.write_text("## Bug Fix\nTest content")
        
        tool_func = None
        for tool in mcp_server._tools.values():
            if tool.name == "suggest_template":
                tool_func = tool.func
                break
        
        if tool_func:
            result = await tool_func(
                "Fixed null pointer exception in user service",
                "bug"
            )
            
            suggestion = json.loads(result)
            assert suggestion["recommended_template"]["filename"] == "bug.md"
            assert "reasoning" in suggestion
    
    @pytest.mark.asyncio
    async def test_suggest_feature(self, mcp_server, tmp_path, monkeypatch):
        """Test suggesting feature template."""
        monkeypatch.setattr('pr_agent.config.settings.TEMPLATES_DIR', tmp_path)
        
        feature_template = tmp_path / "feature.md"
        feature_template.write_text("## Feature\nTest content")
        
        tool_func = None
        for tool in mcp_server._tools.values():
            if tool.name == "suggest_template":
                tool_func = tool.func
                break
        
        if tool_func:
            result = await tool_func(
                "Added new authentication method for API",
                "feature"
            )
            
            suggestion = json.loads(result)
            assert suggestion["recommended_template"]["filename"] == "feature.md"

