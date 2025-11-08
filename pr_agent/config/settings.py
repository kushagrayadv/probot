import os
from pathlib import Path

# Base directory (project root)
BASE_DIR = Path(__file__).parent.parent.parent

# Templates directory
TEMPLATES_DIR = BASE_DIR / "templates"

# Data directory for runtime files
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Events file path
EVENTS_FILE = DATA_DIR / "github_events.json"

# Slack webhook URL
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

