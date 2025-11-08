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
   
   You can configure the application using environment variables or a `.env` file:
   
   ```bash
   # Required: Slack webhook URL
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
   
   # Recommended: GitHub webhook secret for security
   export GITHUB_WEBHOOK_SECRET="your_webhook_secret_from_github"
   
   # Optional: Logging configuration
   export LOG_LEVEL="INFO"           # DEBUG, INFO, WARNING, ERROR, CRITICAL
   export LOG_FORMAT="json"          # "json" for structured logs, "text" for human-readable
   export LOG_FILE="/path/to/logs/app.log"  # Optional: log to file instead of stdout
   ```
   
   **Alternative: `.env` file**: Create a `.env` file in the project root:
   ```bash
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   GITHUB_WEBHOOK_SECRET=your_webhook_secret_from_github
   LOG_LEVEL=INFO
   LOG_FORMAT=json
   LOG_FILE=/path/to/logs/app.log
   ```
   
   **Configuration Management**: The application uses Pydantic Settings for configuration management, which provides:
   - Automatic validation of configuration values
   - Support for environment variables and `.env` files
   - Type safety and IDE autocomplete
   - Case-insensitive environment variable names
   
   **Security Note**: The `GITHUB_WEBHOOK_SECRET` should match the secret configured in your GitHub repository's webhook settings. If not set, webhook signature verification will be disabled (not recommended for production).
   
   **Logging**: The application uses structured JSON logging by default, which is ideal for log aggregation systems. Set `LOG_FORMAT="text"` for human-readable logs during development.

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

### Type Checking

The project uses Pydantic for data validation and includes mypy configuration for type checking:

```bash
# Run type checking
uv run mypy pr_agent

# Run tests
uv run pytest
```

### Async/Await Consistency

The project uses async/await consistently throughout:
- **HTTP requests**: Uses `aiohttp` for all HTTP operations (Slack webhooks, webhook server)
- **Git operations**: Uses `asyncio.create_subprocess_exec` for non-blocking git commands
- **File I/O**: Uses `asyncio.to_thread()` for file operations to avoid blocking the event loop
- **Webhook server**: Fully async using `aiohttp` web framework

This ensures the application remains responsive and can handle concurrent requests efficiently.

## Key Learning Outcomes

This solution demonstrates all MCP primitives working together for real-world team automation.

