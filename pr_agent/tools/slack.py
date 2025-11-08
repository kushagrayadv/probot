from typing import Optional
import asyncio

from mcp.server.fastmcp import FastMCP

from pr_agent.config.settings import SLACK_WEBHOOK_URL
from pr_agent.utils.logger import get_logger
from pr_agent.utils.http_client import default_client
from pr_agent.utils.response_helpers import format_user_message

logger = get_logger(__name__)


def register_slack_tools(mcp: FastMCP) -> None:
    """Register Slack tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance to register tools with
    """
    
    @mcp.tool()
    async def send_slack_notification(message: str) -> str:
        """Send a formatted notification to the team Slack channel.
        
        Args:
            message: The message to send to Slack (supports Slack markdown)
            
        IMPORTANT: For CI failures, use format_ci_failure_alert prompt first!
        IMPORTANT: For deployments, use format_ci_success_summary prompt first!
        """
        webhook_url = SLACK_WEBHOOK_URL
        if not webhook_url:
            logger.error("Slack webhook URL not configured")
            return format_user_message(False, "SLACK_WEBHOOK_URL environment variable not set")
        
        message_length = len(message)
        logger.info(
            "Sending Slack notification",
            message_length=message_length,
            webhook_configured=True
        )
        
        # Prepare the payload with proper Slack formatting
        payload = {
            "text": message,
            "mrkdwn": True
        }
        
        try:
            status_code, response_text = await default_client.post_json(webhook_url, payload)
            
            if status_code == 200:
                logger.info(
                    "Slack notification sent successfully",
                    status_code=status_code,
                    message_length=message_length
                )
                return format_user_message(True, "Message sent successfully to Slack")
            else:
                # Limit response text size for logging
                response_preview = response_text[:200] if response_text else ""
                logger.error(
                    "Failed to send Slack notification",
                    status_code=status_code,
                    response_text=response_preview
                )
                return format_user_message(
                    False,
                    f"Failed to send message. Status: {status_code}, Response: {response_preview}"
                )
        
        except asyncio.TimeoutError:
            logger.error("Slack webhook request timed out", timeout=10)
            return format_user_message(False, "Request timed out. Check your internet connection and try again.")
        except Exception as e:
            logger.exception("Unexpected error sending Slack notification", error=str(e))
            return format_user_message(False, f"Error sending message: {str(e)}")

