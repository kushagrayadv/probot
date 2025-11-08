from pathlib import Path
from typing import Optional, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation and environment variable support.
    
    Settings are loaded from environment variables with the following precedence:
    1. Environment variables
    2. .env file (if present)
    3. Default values
    
    All settings can be overridden via environment variables.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Base directory (project root) - computed, not from env
    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent,
        description="Base directory (project root)"
    )
    
    # Slack configuration
    slack_webhook_url: Optional[str] = Field(
        default=None,
        description="Slack webhook URL for sending notifications"
    )
    
    # GitHub webhook configuration
    github_webhook_secret: str = Field(
        default="",
        description="GitHub webhook secret for signature verification"
    )
    
    # Logging configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    
    log_format: Literal["json", "text"] = Field(
        default="text",
        description="Log format: 'json' for structured logs, 'text' for human-readable"
    )
    
    log_file: Optional[str] = Field(
        default=None,
        description="Optional log file path. If None, logs to stdout"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is uppercase."""
        return v.upper()
    
    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format."""
        v_lower = v.lower()
        if v_lower not in ("json", "text"):
            raise ValueError("log_format must be 'json' or 'text'")
        return v_lower
    
    @property
    def templates_dir(self) -> Path:
        """Templates directory path."""
        return self.base_dir / "templates"
    
    @property
    def data_dir(self) -> Path:
        """Data directory for runtime files."""
        data_dir = self.base_dir / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir
    
    @property
    def events_file(self) -> Path:
        """Events file path."""
        return self.data_dir / "github_events.json"


# Create global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance.
    
    Returns:
        Settings instance (singleton pattern)
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Create settings instance
settings = get_settings()

# Export individual settings for backward compatibility
BASE_DIR: Path = settings.base_dir
TEMPLATES_DIR: Path = settings.templates_dir
DATA_DIR: Path = settings.data_dir
EVENTS_FILE: Path = settings.events_file
SLACK_WEBHOOK_URL: Optional[str] = settings.slack_webhook_url
GITHUB_WEBHOOK_SECRET: str = settings.github_webhook_secret
LOG_LEVEL: str = settings.log_level
LOG_FORMAT: str = settings.log_format
LOG_FILE: Optional[str] = settings.log_file
