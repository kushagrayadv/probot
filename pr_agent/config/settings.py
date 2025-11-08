import os
from pathlib import Path
from typing import Optional

# Base directory (project root)
BASE_DIR: Path = Path(__file__).parent.parent.parent

# Templates directory
TEMPLATES_DIR: Path = BASE_DIR / "templates"

# Data directory for runtime files
DATA_DIR: Path = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Events file path
EVENTS_FILE: Path = DATA_DIR / "github_events.json"

# Slack webhook URL
SLACK_WEBHOOK_URL: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")

# GitHub webhook secret for signature verification
# Set this to the secret configured in your GitHub repository webhook settings
GITHUB_WEBHOOK_SECRET: str = os.getenv("GITHUB_WEBHOOK_SECRET", "")

# Logging configuration
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: str = os.getenv("LOG_FORMAT", "text")  # "json" or "text"
LOG_FILE: Optional[str] = os.getenv("LOG_FILE")  # Optional log file path

