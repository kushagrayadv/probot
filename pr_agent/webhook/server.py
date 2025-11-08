#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from aiohttp import web

from pr_agent.config.settings import (
    GITHUB_WEBHOOK_SECRET,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_FILE
)
from pr_agent.webhook.security import verify_github_signature, get_raw_body
from pr_agent.utils.logger import setup_logging, get_logger
from pr_agent.utils.json_helpers import from_json_string, safe_model_validate
from pr_agent.utils.response_helpers import web_error_response, web_json_response
from pr_agent.db.operations import init_database, insert_event
from pr_agent.models.events import GitHubEvent, WorkflowRun, CheckRun

# Setup logging
setup_logging(level=LOG_LEVEL, format_type=LOG_FORMAT, log_file=Path(LOG_FILE) if LOG_FILE else None)
logger = get_logger(__name__)


async def handle_webhook(request: web.Request) -> web.Response:
    """Handle incoming GitHub webhook with signature verification.
    
    Args:
        request: aiohttp request object
        
    Returns:
        JSON response with status
    """
    event_type: str = request.headers.get("X-GitHub-Event", "unknown")
    remote_addr: Optional[str] = request.remote
    
    logger.info(
        "Webhook request received",
        event_type=event_type,
        remote_addr=remote_addr,
        path=request.path
    )
    
    try:
        # Read raw body first for signature verification
        # This must be done before parsing JSON
        raw_body = await get_raw_body(request)
        
        # Verify webhook signature if secret is configured
        if GITHUB_WEBHOOK_SECRET:
            signature_header = request.headers.get("X-Hub-Signature-256")
            try:
                if not verify_github_signature(raw_body, signature_header, GITHUB_WEBHOOK_SECRET):
                    logger.warning(
                        "Invalid webhook signature",
                        event_type=event_type,
                        remote_addr=remote_addr
                    )
                    return web_error_response(
                        "Invalid webhook signature",
                        status=401,
                        error_code="INVALID_SIGNATURE"
                    )
                logger.debug("Webhook signature verified successfully", event_type=event_type)
            except ValueError as e:
                # Invalid signature format or missing secret
                logger.error(
                    "Signature verification failed",
                    event_type=event_type,
                    remote_addr=remote_addr,
                    error=str(e)
                )
                return web_error_response(
                    f"Signature verification failed: {str(e)}",
                    status=401,
                    error_code="SIGNATURE_VERIFICATION_FAILED"
                )
        
        # Parse JSON from raw body
        data: Dict[str, Any] = from_json_string(raw_body.decode('utf-8'))
        if data is None:
            logger.error(
                "Invalid JSON payload",
                event_type=event_type,
                remote_addr=remote_addr
            )
            return web_error_response(
                "Invalid JSON payload",
                status=400,
                error_code="INVALID_JSON"
            )
        
        # Extract data with validation
        repository: Optional[str] = data.get("repository", {}).get("full_name") if isinstance(data.get("repository"), dict) else None
        action: Optional[str] = data.get("action")
        sender: Optional[str] = data.get("sender", {}).get("login") if isinstance(data.get("sender"), dict) else None
        
        # Parse workflow_run and check_run with Pydantic validation
        workflow_run: Optional[WorkflowRun] = None
        if data.get("workflow_run"):
            workflow_run = safe_model_validate(
                WorkflowRun,
                data["workflow_run"],
                context={"event_type": event_type, "field": "workflow_run"}
            )
        
        check_run: Optional[CheckRun] = None
        if data.get("check_run"):
            check_run = safe_model_validate(
                CheckRun,
                data["check_run"],
                context={"event_type": event_type, "field": "check_run"}
            )
        
        # Create event record with Pydantic model
        try:
            event = GitHubEvent(
                timestamp=datetime.utcnow().isoformat(),
                event_type=event_type,
                action=action,
                workflow_run=workflow_run,
                check_run=check_run,
                repository=repository,
                sender=sender
            )
            # Convert to dict for JSON serialization
            event_dict: Dict[str, Any] = event.model_dump(exclude_none=True)
        except Exception as e:
            logger.error(
                "Failed to create event model",
                error=str(e),
                event_type=event_type
            )
            # Fallback to basic dict structure
            event_dict = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "action": action,
                "workflow_run": data.get("workflow_run"),
                "check_run": data.get("check_run"),
                "repository": repository,
                "sender": sender
            }
        
        logger.info(
            "Processing webhook event",
            event_type=event_type,
            action=action,
            repository=repository,
            sender=sender
        )
        
        # Save event to database
        try:
            # Parse timestamp
            timestamp = datetime.fromisoformat(event_dict["timestamp"].replace('Z', '+00:00'))
            
            # Extract workflow_run and check_run as dicts
            workflow_run_dict = event_dict.get("workflow_run")
            check_run_dict = event_dict.get("check_run")
            
            # Insert into database
            event_id = await insert_event(
                timestamp=timestamp,
                event_type=event_type,
                action=action,
                repository=repository,
                sender=sender,
                workflow_run=workflow_run_dict,
                check_run=check_run_dict,
                raw_payload=data
            )
            
            logger.debug(
                "Event saved to database successfully",
                event_id=event_id,
                event_type=event_type,
                repository=repository
            )
        except Exception as e:
            logger.error(
                "Failed to save event to database",
                error=str(e),
                event_type=event_type,
                repository=repository
            )
            # Continue even if save fails - we still want to return success
        
        logger.info(
            "Webhook processed successfully",
            event_type=event_type,
            repository=repository,
            action=action
        )
        
        return web_json_response({"status": "received"})
    except Exception as e:
        logger.exception(
            "Unexpected error processing webhook",
            event_type=event_type,
            remote_addr=remote_addr,
            error=str(e)
        )
        return web_error_response(
            f"Internal server error: {str(e)}",
            status=500,
            error_code="INTERNAL_ERROR"
        )


# Create app and add route
app = web.Application()

# Initialize database on startup
async def init_app(app: web.Application) -> None:
    """Initialize database on application startup."""
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        # Continue anyway - database might be configured later

# Cleanup on shutdown
async def cleanup_app(app: web.Application) -> None:
    """Cleanup on application shutdown."""
    from pr_agent.db.connection import close_pool
    await close_pool()
    logger.info("Database connection pool closed")

app.on_startup.append(init_app)
app.on_cleanup.append(cleanup_app)
app.router.add_post('/webhook/github', handle_webhook)


if __name__ == '__main__':
    logger.info(
        "Starting webhook server",
        host="localhost",
        port=8080,
        signature_verification="enabled" if GITHUB_WEBHOOK_SECRET else "disabled"
    )
    
    if not GITHUB_WEBHOOK_SECRET:
        logger.warning(
            "Webhook signature verification is disabled",
            message="Set GITHUB_WEBHOOK_SECRET environment variable to enable"
        )
    
    web.run_app(app, host='localhost', port=8080)

