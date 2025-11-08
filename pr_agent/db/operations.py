from datetime import datetime
from typing import Optional, List, Dict, Any
from asyncpg import Connection

from pr_agent.db.connection import get_pool
from pr_agent.db.models import (
    CREATE_TABLE_SQL,
    INSERT_EVENT_SQL,
    GET_RECENT_EVENTS_SQL,
    GET_WORKFLOW_EVENTS_SQL,
    event_to_dict
)
from pr_agent.utils.logger import get_logger

logger = get_logger(__name__)


async def init_database() -> None:
    """Initialize database schema (create table and indexes if they don't exist).
    
    Raises:
        RuntimeError: If database connection fails
    """
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'github_events'
                );
            """)
            
            if not table_exists:
                await conn.execute(CREATE_TABLE_SQL)
                logger.info("Database schema created successfully")
            else:
                logger.debug("Database schema already exists, skipping creation")
    except Exception as e:
        logger.error("Failed to initialize database schema", error=str(e))
        raise RuntimeError(f"Database initialization failed: {str(e)}") from e


async def insert_event(
    timestamp: datetime,
    event_type: str,
    action: Optional[str],
    repository: Optional[str],
    sender: Optional[str],
    workflow_run: Optional[Dict[str, Any]],
    check_run: Optional[Dict[str, Any]],
    raw_payload: Optional[Dict[str, Any]] = None
) -> int:
    """Insert a GitHub event into the database.
    
    Args:
        timestamp: Event timestamp
        action: Event action
        repository: Repository full name
        sender: GitHub username
        workflow_run: Workflow run data (as dict)
        check_run: Check run data (as dict)
        raw_payload: Full webhook payload (optional)
        
    Returns:
        Inserted event ID
        
    Raises:
        RuntimeError: If database operation fails
    """
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            event_id = await conn.fetchval(
                INSERT_EVENT_SQL,
                timestamp,
                event_type,
                action,
                repository,
                sender,
                workflow_run,
                check_run,
                raw_payload
            )
            logger.debug("Event inserted into database", event_id=event_id, event_type=event_type)
            return event_id
    except Exception as e:
        logger.error(
            "Failed to insert event into database",
            error=str(e),
            event_type=event_type,
            repository=repository
        )
        raise RuntimeError(f"Failed to insert event: {str(e)}") from e


async def get_recent_events(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent GitHub events from the database.
    
    Args:
        limit: Maximum number of events to return
        
    Returns:
        List of event dictionaries
    """
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(GET_RECENT_EVENTS_SQL, limit)
            events = [event_to_dict(row) for row in rows]
            logger.debug("Retrieved recent events from database", count=len(events), limit=limit)
            return events
    except Exception as e:
        logger.error("Failed to retrieve recent events from database", error=str(e))
        return []


async def get_workflow_events(workflow_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get workflow events from the database.
    
    Args:
        workflow_name: Optional workflow name to filter by
        
    Returns:
        List of event dictionaries
    """
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(GET_WORKFLOW_EVENTS_SQL, workflow_name)
            events = [event_to_dict(row) for row in rows]
            logger.debug(
                "Retrieved workflow events from database",
                count=len(events),
                workflow_name=workflow_name
            )
            return events
    except Exception as e:
        logger.error("Failed to retrieve workflow events from database", error=str(e))
        return []


async def cleanup_old_events(keep_count: int = 1000) -> int:
    """Delete old events, keeping only the most recent N events.
    
    Args:
        keep_count: Number of recent events to keep
        
    Returns:
        Number of events deleted
    """
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Get the timestamp of the Nth most recent event
            result = await conn.fetchval(
                """
                SELECT timestamp FROM github_events
                ORDER BY timestamp DESC
                OFFSET $1
                LIMIT 1
                """,
                keep_count
            )
            
            if result:
                # Delete events older than that timestamp
                deleted = await conn.execute(
                    """
                    DELETE FROM github_events
                    WHERE timestamp < $1
                    """,
                    result
                )
                deleted_count = int(deleted.split()[-1]) if deleted else 0
                logger.info(
                    "Cleaned up old events",
                    deleted_count=deleted_count,
                    kept_count=keep_count
                )
                return deleted_count
            else:
                logger.debug("No old events to clean up", keep_count=keep_count)
                return 0
    except Exception as e:
        logger.error("Failed to cleanup old events", error=str(e))
        return 0

