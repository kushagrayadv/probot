import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from pr_agent.config.settings import EVENTS_FILE
from pr_agent.utils.logger import get_logger
from pr_agent.utils.file_lock import safe_read_json

logger = get_logger(__name__)


def register_github_actions_tools(mcp: FastMCP):
    """Register GitHub Actions tools with the MCP server."""
    
    @mcp.tool()
    async def get_recent_actions_events(limit: int = 10) -> str:
        """Get recent GitHub Actions events received via webhook.
        
        Args:
            limit: Maximum number of events to return (default: 10)
        """
        logger.debug("Getting recent actions events", limit=limit)
        
        # Read events from file with file locking (safe concurrent access)
        events = safe_read_json(EVENTS_FILE, default=[])
        
        if not events:
            logger.debug("No events found", events_file=str(EVENTS_FILE))
            return json.dumps([])
        
        # Return most recent events
        recent = events[-limit:]
        logger.info(
            "Retrieved recent actions events",
            limit=limit,
            total_events=len(events),
            returned_events=len(recent)
        )
        return json.dumps(recent, indent=2)
    
    
    @mcp.tool()
    async def get_workflow_status(workflow_name: Optional[str] = None) -> str:
        """Get the current status of GitHub Actions workflows.
        
        Args:
            workflow_name: Optional specific workflow name to filter by
        """
        logger.debug("Getting workflow status", workflow_name=workflow_name)
        
        # Read events from file with file locking (safe concurrent access)
        events = safe_read_json(EVENTS_FILE, default=[])
        
        if not events:
            logger.debug("No events found", events_file=str(EVENTS_FILE))
            return json.dumps({"message": "No GitHub Actions events received yet"})
        
        # Filter for workflow events
        workflow_events = [
            e for e in events 
            if e.get("workflow_run") is not None
        ]
        
        if workflow_name:
            workflow_events = [
                e for e in workflow_events
                if e["workflow_run"].get("name") == workflow_name
            ]
            logger.debug("Filtered workflow events", workflow_name=workflow_name, count=len(workflow_events))
        
        # Group by workflow and get latest status
        workflows = {}
        for event in workflow_events:
            run = event["workflow_run"]
            name = run["name"]
            if name not in workflows or run["updated_at"] > workflows[name]["updated_at"]:
                workflows[name] = {
                    "name": name,
                    "status": run["status"],
                    "conclusion": run.get("conclusion"),
                    "run_number": run["run_number"],
                    "updated_at": run["updated_at"],
                    "html_url": run["html_url"]
                }
        
        logger.info(
            "Retrieved workflow status",
            workflow_name=workflow_name,
            workflows_found=len(workflows)
        )
        
        return json.dumps(list(workflows.values()), indent=2)

