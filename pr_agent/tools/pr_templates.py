import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from pr_agent.config.settings import TEMPLATES_DIR
from pr_agent.utils.constants import DEFAULT_TEMPLATES, TYPE_MAPPING
from pr_agent.utils.logger import get_logger

logger = get_logger(__name__)


def register_pr_template_tools(mcp: FastMCP):
    """Register PR template tools with the MCP server."""
    
    @mcp.tool()
    async def get_pr_templates() -> str:
        """List available PR templates with their content."""
        logger.debug("Getting PR templates", templates_dir=str(TEMPLATES_DIR))
        
        templates = []
        for filename, template_type in DEFAULT_TEMPLATES.items():
            template_path = TEMPLATES_DIR / filename
            try:
                content = template_path.read_text()
                templates.append({
                    "filename": filename,
                    "type": template_type,
                    "content": content
                })
            except IOError as e:
                logger.warning(
                    "Failed to read template file",
                    filename=filename,
                    error=str(e)
                )
        
        logger.info("Retrieved PR templates", count=len(templates))
        return json.dumps(templates, indent=2)
    
    
    @mcp.tool()
    async def suggest_template(changes_summary: str, change_type: str) -> str:
        """Let Claude analyze the changes and suggest the most appropriate PR template.
        
        Args:
            changes_summary: Your analysis of what the changes do
            change_type: The type of change you've identified (bug, feature, docs, refactor, test, etc.)
        """
        logger.debug(
            "Suggesting PR template",
            change_type=change_type,
            summary_length=len(changes_summary)
        )
        
        # Get available templates directly (avoid calling tool from within tool)
        templates = []
        for filename, template_type in DEFAULT_TEMPLATES.items():
            template_path = TEMPLATES_DIR / filename
            try:
                content = template_path.read_text()
                templates.append({
                    "filename": filename,
                    "type": template_type,
                    "content": content
                })
            except IOError as e:
                logger.warning(
                    "Failed to read template file",
                    filename=filename,
                    error=str(e)
                )
        
        if not templates:
            logger.error("No templates available")
            raise ValueError("No PR templates found")
        
        # Find matching template
        template_file = TYPE_MAPPING.get(change_type.lower(), "feature.md")
        selected_template = next(
            (t for t in templates if t["filename"] == template_file),
            templates[0]  # Default to first template if no match
        )
        
        logger.info(
            "Template suggested",
            change_type=change_type,
            selected_template=selected_template["filename"],
            template_type=selected_template["type"]
        )
        
        suggestion = {
            "recommended_template": selected_template,
            "reasoning": f"Based on your analysis: '{changes_summary}', this appears to be a {change_type} change.",
            "template_content": selected_template["content"],
            "usage_hint": "Claude can help you fill out this template based on the specific changes in your PR."
        }
        
        return json.dumps(suggestion, indent=2)

