#!/usr/bin/env python3
"""
Module 3: Slack Notification Integration - Complete Solution
Combines all MCP primitives (Tools and Prompts) for complete team communication workflows.
"""

from mcp.server.fastmcp import FastMCP

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


if __name__ == "__main__":
    # Run MCP server normally
    print("Starting PR Agent Slack MCP server...")
    print("Make sure to set SLACK_WEBHOOK_URL environment variable")
    print("To receive GitHub webhooks, run the webhook server separately:")
    print("  python -m pr_agent.webhook.server")
    mcp.run()

