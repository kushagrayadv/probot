"""Deployment prompts."""

from mcp.server.fastmcp import FastMCP


def register_deployment_prompts(mcp: FastMCP):
    """Register deployment prompts with the MCP server."""
    
    @mcp.prompt()
    async def create_deployment_summary():
        """Generate a deployment summary for team communication."""
        return """Create a deployment summary for team communication:

1. Check workflow status with get_workflow_status()
2. Look specifically for deployment-related workflows
3. Note the deployment outcome, timing, and any issues

Format as a concise message suitable for Slack:

🚀 *Deployment Update*
- *Status*: [✅ Success / ❌ Failed / ⏳ In Progress]
- *Environment*: [Production/Staging/Dev]
- *Version/Commit*: [If available from workflow data]
- *Duration*: [If available]
- *Key Changes*: [Brief summary if available]
- *Issues*: [Any problems encountered]
- *Next Steps*: [Required actions if failed]

Keep it brief but informative for team awareness."""

