import os
from typing import Optional
import requests

from mcp.server.fastmcp import FastMCP

from pr_agent.config.settings import SLACK_WEBHOOK_URL
from pr_agent.utils.logger import get_logger

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
        webhook_url = SLACK_WEBHOOK_URL or os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            logger.error("Slack webhook URL not configured")
            return "Error: SLACK_WEBHOOK_URL environment variable not set"
        
        message_length = len(message)
        logger.info(
            "Sending Slack notification",
            message_length=message_length,
            webhook_configured=True
        )
        
        try:
            # Prepare the payload with proper Slack formatting
            payload = {
                "text": message,
                "mrkdwn": True
            }
            
            # Send POST request to Slack webhook
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            
            # Check if request was successful
            if response.status_code == 200:
                logger.info(
                    "Slack notification sent successfully",
                    status_code=response.status_code,
                    message_length=message_length
                )
                return "✅ Message sent successfully to Slack"
            else:
                logger.error(
                    "Failed to send Slack notification",
                    status_code=response.status_code,
                    response_text=response.text[:200]  # Limit log size
                )
                return f"❌ Failed to send message. Status: {response.status_code}, Response: {response.text}"
            
        except requests.exceptions.Timeout:
            logger.error("Slack webhook request timed out", timeout=10)
            return "❌ Request timed out. Check your internet connection and try again."
        except requests.exceptions.ConnectionError as e:
            logger.error("Slack webhook connection error", error=str(e))
            return "❌ Connection error. Check your internet connection and webhook URL."
        except Exception as e:
            logger.exception("Unexpected error sending Slack notification", error=str(e))
            return f"❌ Error sending message: {str(e)}"

