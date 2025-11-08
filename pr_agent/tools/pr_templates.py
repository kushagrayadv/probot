"""PR template tools."""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from pr_agent.config.settings import TEMPLATES_DIR
from pr_agent.utils.constants import DEFAULT_TEMPLATES, TYPE_MAPPING


def register_pr_template_tools(mcp: FastMCP):
    """Register PR template tools with the MCP server."""
    
    @mcp.tool()
    async def get_pr_templates() -> str:
        """List available PR templates with their content."""
        templates = [
            {
                "filename": filename,
                "type": template_type,
                "content": (TEMPLATES_DIR / filename).read_text()
            }
            for filename, template_type in DEFAULT_TEMPLATES.items()
        ]
        
        return json.dumps(templates, indent=2)
    
    
    @mcp.tool()
    async def suggest_template(changes_summary: str, change_type: str) -> str:
        """Let Claude analyze the changes and suggest the most appropriate PR template.
        
        Args:
            changes_summary: Your analysis of what the changes do
            change_type: The type of change you've identified (bug, feature, docs, refactor, test, etc.)
        """
        
        # Get available templates directly (avoid calling tool from within tool)
        templates = [
            {
                "filename": filename,
                "type": template_type,
                "content": (TEMPLATES_DIR / filename).read_text()
            }
            for filename, template_type in DEFAULT_TEMPLATES.items()
        ]
        
        # Find matching template
        template_file = TYPE_MAPPING.get(change_type.lower(), "feature.md")
        selected_template = next(
            (t for t in templates if t["filename"] == template_file),
            templates[0]  # Default to first template if no match
        )
        
        suggestion = {
            "recommended_template": selected_template,
            "reasoning": f"Based on your analysis: '{changes_summary}', this appears to be a {change_type} change.",
            "template_content": selected_template["content"],
            "usage_hint": "Claude can help you fill out this template based on the specific changes in your PR."
        }
        
        return json.dumps(suggestion, indent=2)

