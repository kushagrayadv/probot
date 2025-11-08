# Module 3: Slack Notification - Complete Solution

This is the complete implementation of Module 3, demonstrating how to integrate MCP Tools and Prompts for team communication via Slack.

## What This Implements

This solution extends Modules 1 and 2 with:

1. **`send_slack_notification` tool** - Sends formatted messages to Slack via webhook with proper error handling
2. **`format_ci_failure_alert` prompt** - Creates rich failure alerts with Slack markdown
3. **`format_ci_success_summary` prompt** - Creates celebration messages for successful deployments

## Setup and Usage

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up environment variables:
   ```bash
   # Required: Slack webhook URL
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
   
   # Recommended: GitHub webhook secret for security
   export GITHUB_WEBHOOK_SECRET="your_webhook_secret_from_github"
   ```
   
   **Security Note**: The `GITHUB_WEBHOOK_SECRET` should match the secret configured in your GitHub repository's webhook settings. If not set, webhook signature verification will be disabled (not recommended for production).

3. Start services:
   ```bash
   # Terminal 1: Webhook server
   python -m pr_agent.webhook.server
   
   # Terminal 2: MCP server
   uv run pr_agent.server
   
   # Terminal 3: Cloudflare tunnel (optional)
   cloudflared tunnel --url http://localhost:8080
   ```

## Testing

See `docs/manual_test.md` for comprehensive testing instructions using curl commands to simulate GitHub webhook events.

## Key Learning Outcomes

This solution demonstrates all MCP primitives working together for real-world team automation.

