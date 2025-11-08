import pytest
from pathlib import Path
from pr_agent.config.settings import Settings, get_settings


class TestSettings:
    """Tests for the Settings Pydantic model."""

    def test_default_settings(self):
        """Test default settings values."""
        # Create a fresh settings instance
        settings = Settings()
        
        assert settings.log_level == "INFO"
        assert settings.log_format == "text"
        assert settings.log_file is None
        assert settings.github_webhook_secret == ""
        assert settings.slack_webhook_url is None
        assert isinstance(settings.base_dir, Path)
        assert settings.base_dir.exists()

    def test_settings_from_env(self, monkeypatch):
        """Test settings loaded from environment variables."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("LOG_FORMAT", "json")
        monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/test")
        monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test_secret")
        
        # Create new settings instance to pick up env vars
        settings = Settings()
        
        assert settings.log_level == "DEBUG"
        assert settings.log_format == "json"
        assert settings.slack_webhook_url == "https://hooks.slack.com/test"
        assert settings.github_webhook_secret == "test_secret"

    def test_log_level_validation(self, monkeypatch):
        """Test log level validation."""
        monkeypatch.setenv("LOG_LEVEL", "debug")  # lowercase
        settings = Settings()
        # Should be converted to uppercase
        assert settings.log_level == "DEBUG"

    def test_log_format_validation(self):
        """Test log format validation."""
        # Valid formats
        settings1 = Settings(log_format="json")
        assert settings1.log_format == "json"
        
        settings2 = Settings(log_format="TEXT")  # uppercase
        assert settings2.log_format == "text"  # converted to lowercase
        
        # Invalid format should raise error
        with pytest.raises(ValueError, match="log_format must be 'json' or 'text'"):
            Settings(log_format="invalid")

    def test_computed_properties(self):
        """Test computed path properties."""
        settings = Settings()
        
        assert isinstance(settings.templates_dir, Path)
        assert settings.templates_dir == settings.base_dir / "templates"
        
        assert isinstance(settings.data_dir, Path)
        assert settings.data_dir == settings.base_dir / "data"
        # data_dir should be created
        assert settings.data_dir.exists()
        
        assert isinstance(settings.events_file, Path)
        assert settings.events_file == settings.data_dir / "github_events.json"

    def test_singleton_pattern(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Should be the same instance (singleton)
        assert settings1 is settings2

    def test_case_insensitive_env_vars(self, monkeypatch):
        """Test that environment variables are case-insensitive."""
        monkeypatch.setenv("log_level", "WARNING")
        monkeypatch.setenv("LOG_FORMAT", "json")
        
        settings = Settings()
        
        assert settings.log_level == "WARNING"
        assert settings.log_format == "json"

    def test_optional_fields(self):
        """Test that optional fields can be None."""
        settings = Settings()
        
        assert settings.slack_webhook_url is None or isinstance(settings.slack_webhook_url, str)
        assert settings.log_file is None or isinstance(settings.log_file, str)

