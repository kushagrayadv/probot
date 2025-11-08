"""Slack notification tools."""

import os
import requests

from mcp.server.fastmcp import FastMCP

from pr_agent.config.settings import SLACK_WEBHOOK_URL


def register_slack_tools(mcp: FastMCP):
    """Register Slack tools with the MCP server."""
    
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
            return "Error: SLACK_WEBHOOK_URL environment variable not set"
        
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
                return "✅ Message sent successfully to Slack"
            else:
                return f"❌ Failed to send message. Status: {response.status_code}, Response: {response.text}"
            
        except requests.exceptions.Timeout:
            return "❌ Request timed out. Check your internet connection and try again."
        except requests.exceptions.ConnectionError:
            return "❌ Connection error. Check your internet connection and webhook URL."
        except Exception as e:
            return f"❌ Error sending message: {str(e)}"

