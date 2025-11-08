import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add module and function information
        if record.module:
            log_data["module"] = record.module
        if record.funcName:
            log_data["function"] = record.funcName
        if record.lineno:
            log_data["line"] = record.lineno
        
        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields from the log record
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName", "relativeCreated",
                "thread", "threadName", "exc_info", "exc_text", "stack_info"
            ):
                log_data[key] = value
        
        return json.dumps(log_data, default=str)


class StructuredLogger:
    """Wrapper for structured logging with context support."""
    
    def __init__(self, name: str):
        """Initialize logger with given name."""
        self.logger = logging.getLogger(name)
    
    def _log_with_context(
        self,
        level: int,
        message: str,
        *args,
        **kwargs
    ) -> None:
        """Log message with additional context."""
        extra = kwargs.pop("extra", {})
        if kwargs:
            extra.update(kwargs)
        self.logger.log(level, message, *args, extra=extra)
    
    def debug(self, message: str, **context) -> None:
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, message, extra=context)
    
    def info(self, message: str, **context) -> None:
        """Log info message with context."""
        self._log_with_context(logging.INFO, message, extra=context)
    
    def warning(self, message: str, **context) -> None:
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, message, extra=context)
    
    def error(self, message: str, **context) -> None:
        """Log error message with context."""
        self._log_with_context(logging.ERROR, message, extra=context)
    
    def exception(self, message: str, **context) -> None:
        """Log exception with traceback and context."""
        self.logger.exception(message, extra=context)
    
    def critical(self, message: str, **context) -> None:
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, message, extra=context)


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    log_file: Optional[Path] = None
) -> None:
    """Configure logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type - "json" for structured JSON, "text" for human-readable
        log_file: Optional path to log file. If None, logs to stdout
    """
    # Convert string level to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    if format_type == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Create handler
    if log_file:
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler(sys.stdout)
    
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    
    # Add handler to root logger
    root_logger.addHandler(handler)
    
    # Set level for third-party loggers to WARNING to reduce noise
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)

