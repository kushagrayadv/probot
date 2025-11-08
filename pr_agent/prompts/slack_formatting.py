from mcp.server.fastmcp import FastMCP


def register_slack_formatting_prompts(mcp: FastMCP) -> None:
    """Register Slack formatting prompts with the MCP server.
    
    Args:
        mcp: FastMCP server instance to register prompts with
    """
    
    @mcp.prompt()
    async def format_ci_failure_alert() -> str:
        """Create a Slack alert for CI/CD failures with rich formatting.
        
        Returns:
            Prompt template string for formatting CI failure alerts
        """
        return """Format this GitHub Actions failure as a Slack message using ONLY Slack markdown syntax:

:rotating_light: *CI Failure Alert* :rotating_light:

A CI workflow has failed:
*Workflow*: workflow_name
*Branch*: branch_name
*Status*: Failed
*View Details*: <https://github.com/test/repo/actions/runs/123|View Logs>

Please check the logs and address any issues.

CRITICAL: Use EXACT Slack link format: <https://full-url|Link Text>
Examples:
- CORRECT: <https://github.com/user/repo|Repository>
- WRONG: [Repository](https://github.com/user/repo)
- WRONG: https://github.com/user/repo

Slack formatting rules:
- *text* for bold (NOT **text**)
- `text` for code
- > text for quotes
- Use simple bullet format without special characters
- :emoji_name: for emojis"""
    
    
    @mcp.prompt()
    async def format_ci_success_summary() -> str:
        """Create a Slack message celebrating successful deployments.
        
        Returns:
            Prompt template string for formatting CI success summaries
        """
        return """Format this successful GitHub Actions run as a Slack message using ONLY Slack markdown syntax:

:white_check_mark: *Deployment Successful* :white_check_mark:

Deployment completed successfully for [Repository Name]

*Changes:*
- Key feature or fix 1
- Key feature or fix 2

*Links:*
<https://github.com/user/repo|View Changes>

CRITICAL: Use EXACT Slack link format: <https://full-url|Link Text>
Examples:
- CORRECT: <https://github.com/user/repo|Repository>
- WRONG: [Repository](https://github.com/user/repo)
- WRONG: https://github.com/user/repo

Slack formatting rules:
- *text* for bold (NOT **text**)
- `text` for code
- > text for quotes
- Use simple bullet format with - or *
- :emoji_name: for emojis"""

