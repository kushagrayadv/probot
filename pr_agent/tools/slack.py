import os
from typing import Optional
import aiohttp
import asyncio

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
        
        # Prepare the payload with proper Slack formatting
        payload = {
            "text": message,
            "mrkdwn": True
        }
        
        # Create timeout for the request
        timeout = aiohttp.ClientTimeout(total=10)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_text = await response.text()
                    
                    # Check if request was successful
                    if response.status == 200:
                        logger.info(
                            "Slack notification sent successfully",
                            status_code=response.status,
                            message_length=message_length
                        )
                        return "✅ Message sent successfully to Slack"
                    else:
                        # Limit response text size for logging
                        response_preview = response_text[:200] if response_text else ""
                        logger.error(
                            "Failed to send Slack notification",
                            status_code=response.status,
                            response_text=response_preview
                        )
                        return f"❌ Failed to send message. Status: {response.status}, Response: {response_preview}"
        
        except asyncio.TimeoutError:
            logger.error("Slack webhook request timed out", timeout=10)
            return "❌ Request timed out. Check your internet connection and try again."
        except aiohttp.ClientError as e:
            logger.error("Slack webhook connection error", error=str(e))
            return f"❌ Connection error: {str(e)}. Check your internet connection and webhook URL."
        except Exception as e:
            logger.exception("Unexpected error sending Slack notification", error=str(e))
            return f"❌ Error sending message: {str(e)}"

