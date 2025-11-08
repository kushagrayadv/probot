import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from pr_agent.config.settings import EVENTS_FILE
from pr_agent.db.operations import init_database, insert_event
from pr_agent.utils.logger import get_logger
from pr_agent.utils.file_lock import safe_read_json

logger = get_logger(__name__)


async def migrate_json_to_db(events_file: Path = EVENTS_FILE, dry_run: bool = False) -> int:
    """Migrate events from JSON file to PostgreSQL database.
    
    Args:
        events_file: Path to JSON file containing events
        dry_run: If True, only report what would be migrated without actually migrating
        
    Returns:
        Number of events migrated
    """
    if not events_file.exists():
        logger.info("No JSON file found, nothing to migrate", events_file=str(events_file))
        return 0
    
    logger.info("Starting migration from JSON to database", events_file=str(events_file), dry_run=dry_run)
    
    # Read events from JSON file
    events_data: List[Dict[str, Any]] = safe_read_json(events_file, default=[])
    
    if not events_data:
        logger.info("JSON file is empty, nothing to migrate")
        return 0
    
    logger.info("Found events in JSON file", count=len(events_data))
    
    if dry_run:
        logger.info("DRY RUN: Would migrate events", count=len(events_data))
        return len(events_data)
    
    # Initialize database
    try:
        await init_database()
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise
    
    # Migrate events
    migrated_count = 0
    failed_count = 0
    
    for event_data in events_data:
        try:
            # Parse timestamp
            timestamp_str = event_data.get("timestamp", datetime.utcnow().isoformat())
            try:
                if isinstance(timestamp_str, str):
                    # Handle ISO format with or without timezone
                    if timestamp_str.endswith('Z'):
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        timestamp = datetime.fromisoformat(timestamp_str)
                else:
                    timestamp = datetime.utcnow()
            except (ValueError, TypeError):
                timestamp = datetime.utcnow()
            
            # Extract event data
            event_type = event_data.get("event_type", "unknown")
            action = event_data.get("action")
            repository = event_data.get("repository")
            sender = event_data.get("sender")
            workflow_run = event_data.get("workflow_run")
            check_run = event_data.get("check_run")
            
            # Insert into database
            await insert_event(
                timestamp=timestamp,
                event_type=event_type,
                action=action,
                repository=repository,
                sender=sender,
                workflow_run=workflow_run,
                check_run=check_run,
                raw_payload=event_data
            )
            
            migrated_count += 1
            
        except Exception as e:
            failed_count += 1
            logger.warning(
                "Failed to migrate event",
                error=str(e),
                event_type=event_data.get("event_type"),
                timestamp=event_data.get("timestamp")
            )
    
    logger.info(
        "Migration completed",
        migrated_count=migrated_count,
        failed_count=failed_count,
        total_events=len(events_data)
    )
    
    return migrated_count


if __name__ == "__main__":
    import asyncio
    
    async def main():
        """Run migration."""
        import sys
        dry_run = "--dry-run" in sys.argv
        
        try:
            count = await migrate_json_to_db(dry_run=dry_run)
            print(f"Migration {'would migrate' if dry_run else 'migrated'} {count} events")
        except Exception as e:
            print(f"Migration failed: {e}", file=sys.stderr)
            sys.exit(1)
    
    asyncio.run(main())

