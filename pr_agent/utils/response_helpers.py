from typing import Any, Dict, Optional
from aiohttp import web

from pr_agent.utils.logger import get_logger
from pr_agent.utils.json_helpers import to_json_string

logger = get_logger(__name__)


def success_response(message: str = "Success", data: Optional[Dict[str, Any]] = None) -> str:
    """Format a success response for MCP tools.
    
    Args:
        message: Success message
        data: Optional data to include in response
        
    Returns:
        Formatted success response string
    """
    response: Dict[str, Any] = {
        "status": "success",
        "message": message
    }
    if data:
        response["data"] = data
    
    return to_json_string(response)


def error_response(message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> str:
    """Format an error response for MCP tools.
    
    Args:
        message: Error message
        error_code: Optional error code
        details: Optional error details
        
    Returns:
        Formatted error response string
    """
    response: Dict[str, Any] = {
        "status": "error",
        "message": message
    }
    if error_code:
        response["error_code"] = error_code
    if details:
        response["details"] = details
    
    return to_json_string(response)


def web_json_response(
    data: Dict[str, Any],
    status: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> web.Response:
    """Create a JSON response for aiohttp web handlers.
    
    Args:
        data: Response data dictionary
        status: HTTP status code (default: 200)
        headers: Optional HTTP headers
        
    Returns:
        aiohttp JSON response
    """
    return web.json_response(data, status=status, headers=headers)


def web_error_response(
    message: str,
    status: int = 500,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> web.Response:
    """Create an error JSON response for aiohttp web handlers.
    
    Args:
        message: Error message
        status: HTTP status code (default: 500)
        error_code: Optional error code
        details: Optional error details
        
    Returns:
        aiohttp JSON error response
    """
    error_data: Dict[str, Any] = {"error": message}
    if error_code:
        error_data["error_code"] = error_code
    if details:
        error_data["details"] = details
    
    return web_json_response(error_data, status=status)


def format_user_message(success: bool, message: str, emoji: bool = True) -> str:
    """Format a user-friendly message with optional emoji.
    
    Args:
        success: Whether the operation was successful
        message: Message text
        emoji: Whether to include emoji prefix
        
    Returns:
        Formatted message string
    """
    if emoji:
        prefix = "✅ " if success else "❌ "
        return f"{prefix}{message}"
    return message

