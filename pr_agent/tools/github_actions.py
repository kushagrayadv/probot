from typing import Optional, List, Dict, Any

from mcp.server.fastmcp import FastMCP

from pr_agent.config.settings import EVENTS_FILE
from pr_agent.utils.logger import get_logger
from pr_agent.utils.file_lock import safe_read_json
from pr_agent.utils.json_helpers import to_json_string, validate_models_batch
from pr_agent.models.events import GitHubEvent, WorkflowStatus

logger = get_logger(__name__)


def register_github_actions_tools(mcp: FastMCP) -> None:
    """Register GitHub Actions tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance to register tools with
    """
    
    @mcp.tool()
    async def get_recent_actions_events(limit: int = 10) -> str:
        """Get recent GitHub Actions events received via webhook.
        
        Args:
            limit: Maximum number of events to return (default: 10)
        """
        logger.debug("Getting recent actions events", limit=limit)
        
        # Read events from file with file locking (safe concurrent access)
        events_raw: List[Dict[str, Any]] = safe_read_json(EVENTS_FILE, default=[])
        
        if not events_raw:
            logger.debug("No events found", events_file=str(EVENTS_FILE))
            return to_json_string([])
        
        # Validate and parse events with Pydantic using utility function
        events: List[GitHubEvent] = validate_models_batch(
            GitHubEvent,
            events_raw,
            context={"operation": "get_recent_actions_events"}
        )
        
        # Return most recent events
        recent_events: List[GitHubEvent] = events[-limit:]
        
        logger.info(
            "Retrieved recent actions events",
            limit=limit,
            total_events=len(events),
            returned_events=len(recent_events)
        )
        return to_json_string(recent_events)
    
    
    @mcp.tool()
    async def get_workflow_status(workflow_name: Optional[str] = None) -> str:
        """Get the current status of GitHub Actions workflows.
        
        Args:
            workflow_name: Optional specific workflow name to filter by
            
        Returns:
            JSON string with workflow status information
        """
        logger.debug("Getting workflow status", workflow_name=workflow_name)
        
        # Read events from file with file locking (safe concurrent access)
        events_raw: List[Dict[str, Any]] = safe_read_json(EVENTS_FILE, default=[])
        
        if not events_raw:
            logger.debug("No events found", events_file=str(EVENTS_FILE))
            return to_json_string({"message": "No GitHub Actions events received yet"})
        
        # Validate and parse events with Pydantic using utility function
        events: List[GitHubEvent] = validate_models_batch(
            GitHubEvent,
            events_raw,
            context={"operation": "get_workflow_status"}
        )
        
        # Filter for workflow events
        workflow_events: List[GitHubEvent] = [
            e for e in events 
            if e.workflow_run is not None
        ]
        
        if workflow_name:
            workflow_events = [
                e for e in workflow_events
                if e.workflow_run and e.workflow_run.name == workflow_name
            ]
            logger.debug("Filtered workflow events", workflow_name=workflow_name, count=len(workflow_events))
        
        # Group by workflow and get latest status
        workflows: Dict[str, WorkflowStatus] = {}
        for event in workflow_events:
            if not event.workflow_run:
                continue
                
            run = event.workflow_run
            name = run.name
            
            # Get updated_at for comparison (use timestamp if updated_at is None)
            updated_at = run.updated_at or event.timestamp
            
            if name not in workflows or updated_at > workflows[name].updated_at:
                workflows[name] = WorkflowStatus(
                    name=name,
                    status=run.status,
                    conclusion=run.conclusion,
                    run_number=run.run_number,
                    updated_at=updated_at,
                    html_url=run.html_url
                )
        
        # Convert to list for JSON serialization
        workflows_list: List[WorkflowStatus] = list(workflows.values())
        
        logger.info(
            "Retrieved workflow status",
            workflow_name=workflow_name,
            workflows_found=len(workflows_list)
        )
        
        return to_json_string(workflows_list)

