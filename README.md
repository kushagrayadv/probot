# PRobot: Context-Aware PR Automation Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive **Model Context Protocol (MCP) server** that integrates GitHub webhooks, CI/CD monitoring, and Slack notifications to automate PR workflows and team communication.


## Overview

PRobot is an MCP server that bridges GitHub Actions, Git repositories, and Slack to provide:

- **Automated PR Analysis**: Analyze code changes, suggest templates, and generate status reports
- **CI/CD Monitoring**: Track GitHub Actions workflows and notify teams of failures/successes
- **Slack Integration**: Send formatted notifications to Slack channels
- **Webhook Processing**: Securely receive and process GitHub webhook events
- **Database Storage**: Persistent storage of events in PostgreSQL

The server exposes **Tools** (executable functions) and **Prompts** (templates for AI interactions) that can be used by AI assistants like Claude to help with PR workflows.


## Architecture

```
┌─────────────────┐
│  GitHub Actions │
│   (Webhooks)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐      ┌─────────────┐
│  Webhook Server │─────▶│  PostgreSQL  │      │   Slack     │
│   (aiohttp)     │      │   Database   │      │  Webhooks   │
└────────┬────────┘      └──────────────┘      └─────────────┘
         │
         ▼
┌─────────────────┐
│   MCP Server    │
│  (FastMCP)      │
│                 │
│  ┌───────────┐  │
│  │  Tools    │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │  Prompts  │  │
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Assistant   │
│   (Claude)      │
└─────────────────┘
```

## Installation

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12+ (for event storage)
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

### Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd probot

# Install dependencies using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

## Configuration

### Quick Start

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your configuration:**
   ```bash
   # Required
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   DATABASE_URL=postgresql://user:password@localhost:5432/pr_agent_db
   
   # Recommended
   GITHUB_WEBHOOK_SECRET=your_webhook_secret_from_github
   ```

### Database Setup

1. **Create PostgreSQL database:**
   ```bash
   createdb pr_agent_db
   # Or using psql
   psql -U postgres -c "CREATE DATABASE pr_agent_db;"
   ```

2. **Migrate existing data (if you have JSON file with events):**
   ```bash
   # Dry run to see what would be migrated
   python -m pr_agent.db.migrate --dry-run
   
   # Actually migrate
   python -m pr_agent.db.migrate
   ```

The database schema (table and indexes) is automatically created on first use.

## Usage

### Starting the Services

1. **Start the webhook server** (Terminal 1):
   ```bash
   python -m pr_agent.webhook.server
   ```
   The server runs on `http://localhost:8080` by default.

2. **Start the MCP server** (Terminal 2):
   ```bash
   uv run pr_agent.server
   ```

### Configuring GitHub Webhook

1. Go to your GitHub repository → Settings → Webhooks
2. Add a new webhook:
   - **Payload URL**: `https://your-tunnel-url/webhook/github` (or `http://localhost:8080/webhook/github` for local testing)
   - **Content type**: `application/json`
   - **Secret**: Set `GITHUB_WEBHOOK_SECRET` in your `.env` file
   - **Events**: Select `Workflow runs` and `Check runs`

### Using with Claude Code

1. Configure Claude Code to use this MCP server
2. The server exposes all tools and prompts automatically
3. Ask Claude to:
   - "Analyze the changes in this PR"
   - "Check the CI/CD status"
   - "Send a Slack notification about the deployment"
   - "Generate a PR status report"

## MCP Tools & Prompts

### Tools

`analyze_file_changes`
Analyze git repository changes and generate a diff report.


`get_pr_templates`
List all available PR templates with their content.

`suggest_template`
Suggest the most appropriate PR template based on changes.

`get_recent_actions_events`
Get recent GitHub Actions events from the database.

`get_workflow_status`
Get the current status of GitHub Actions workflows.

`send_slack_notification`
Send a formatted message to Slack.

### Prompts

`format_ci_failure_alert`
Template for formatting CI failure alerts with Slack markdown.

`format_ci_success_summary`
Template for formatting deployment success messages.

`analyze_ci_results`
Template for analyzing CI/CD results and providing insights.

`suggest_ci_improvements`
Template for suggesting CI/CD improvements.

`create_deployment_summary`
Template for creating deployment summaries.

`generate_pr_status_report`
Template for generating comprehensive PR status reports.

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_models.py

# Run with coverage
uv run pytest --cov=pr_agent
```

### Manual Testing

See [`docs/manual_test.md`](docs/manual_test.md) for comprehensive testing instructions using curl commands to simulate GitHub webhook events.

### Type Checking

```bash
# Run mypy type checking
uv run mypy pr_agent
```

## Development

### Adding New Tools

1. Create a function in `pr_agent/tools/`
2. Decorate with `@mcp.tool()`
3. Register in `pr_agent/server.py`

Example:
```python
@mcp.tool()
async def my_new_tool(param: str) -> str:
    """Tool description."""
    # Implementation
    return result
```

### Adding New Prompts

1. Create a function in `pr_agent/prompts/`
2. Decorate with `@mcp.prompt()`
3. Return a prompt template string
4. Register in `pr_agent/server.py`
