#!/usr/bin/env python3

from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Import configuration and logging
from pr_agent.config.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE
from pr_agent.utils.logger import setup_logging, get_logger

# Setup logging first
setup_logging(level=LOG_LEVEL, format_type=LOG_FORMAT, log_file=Path(LOG_FILE) if LOG_FILE else None)
logger = get_logger(__name__)

# Import tool registrations
from pr_agent.tools.git_analysis import register_git_analysis_tools
from pr_agent.tools.pr_templates import register_pr_template_tools
from pr_agent.tools.github_actions import register_github_actions_tools
from pr_agent.tools.slack import register_slack_tools

# Import prompt registrations
from pr_agent.prompts.slack_formatting import register_slack_formatting_prompts
from pr_agent.prompts.ci_analysis import register_ci_analysis_prompts
from pr_agent.prompts.deployment import register_deployment_prompts
from pr_agent.prompts.pr_reports import register_pr_report_prompts

# Initialize the FastMCP server
mcp = FastMCP("pr-agent-slack")

# Register all tools
register_git_analysis_tools(mcp)
register_pr_template_tools(mcp)
register_github_actions_tools(mcp)
register_slack_tools(mcp)

# Register all prompts
register_slack_formatting_prompts(mcp)
register_ci_analysis_prompts(mcp)
register_deployment_prompts(mcp)
register_pr_report_prompts(mcp)

logger.info(
    "MCP server initialized",
    server_name="pr-agent-slack",
    tools_registered=len(mcp._tools) if hasattr(mcp, '_tools') else 0,
    prompts_registered=len(mcp._prompts) if hasattr(mcp, '_prompts') else 0
)


if __name__ == "__main__":
    # Run MCP server normally
    logger.info(
        "Starting PR Agent Slack MCP server",
        message="Make sure to set SLACK_WEBHOOK_URL environment variable",
        webhook_server_command="python -m pr_agent.webhook.server"
    )
    mcp.run()

