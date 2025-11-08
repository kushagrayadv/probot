from datetime import datetime
from typing import Optional, Dict, Any
import json


# SQL schema for creating the github_events table
CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS github_events (
        id BIGSERIAL PRIMARY KEY,
        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
        event_type VARCHAR(100) NOT NULL,
        action VARCHAR(100),
        repository VARCHAR(255),
        sender VARCHAR(255),
        workflow_run JSONB,
        check_run JSONB,
        raw_payload JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_github_events_timestamp ON github_events(timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_github_events_event_type ON github_events(event_type);
    CREATE INDEX IF NOT EXISTS idx_github_events_repository ON github_events(repository);
    CREATE INDEX IF NOT EXISTS idx_github_events_workflow_name ON github_events((workflow_run->>'name'));
"""


# SQL for inserting an event
INSERT_EVENT_SQL = """
    INSERT INTO github_events (
        timestamp, event_type, action, repository, sender,
        workflow_run, check_run, raw_payload
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    RETURNING id;
"""


# SQL for getting recent events
GET_RECENT_EVENTS_SQL = """
    SELECT 
        id,
        timestamp,
        event_type,
        action,
        repository,
        sender,
        workflow_run,
        check_run,
        raw_payload,
        created_at
    FROM github_events
    ORDER BY timestamp DESC
    LIMIT $1;
"""


# SQL for getting workflow events
GET_WORKFLOW_EVENTS_SQL = """
    SELECT 
        id,
        timestamp,
        event_type,
        action,
        repository,
        sender,
        workflow_run,
        check_run,
        raw_payload,
        created_at
    FROM github_events
    WHERE workflow_run IS NOT NULL
        AND ($1::text IS NULL OR workflow_run->>'name' = $1)
    ORDER BY timestamp DESC;
"""


# SQL for getting events by repository
GET_EVENTS_BY_REPOSITORY_SQL = """
    SELECT 
        id,
        timestamp,
        event_type,
        action,
        repository,
        sender,
        workflow_run,
        check_run,
        raw_payload,
        created_at
    FROM github_events
    WHERE repository = $1
    ORDER BY timestamp DESC
    LIMIT $2;
"""


def event_to_dict(row: tuple) -> Dict[str, Any]:
    """Convert database row to dictionary format compatible with GitHubEvent model.

    Args:
        row: Database row tuple

    Returns:
        Dictionary with event data
    """
    return {
        "timestamp": row[1].isoformat() if isinstance(row[1], datetime) else str(row[1]),
        "event_type": row[2],
        "action": row[3],
        "repository": row[4],
        "sender": row[5],
        "workflow_run": row[6],
        "check_run": row[7],
        "raw_payload": row[8],
    }
