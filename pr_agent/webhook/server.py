#!/usr/bin/env python3

import json
from datetime import datetime
from pathlib import Path
from aiohttp import web

from pr_agent.config.settings import EVENTS_FILE, GITHUB_WEBHOOK_SECRET
from pr_agent.webhook.security import verify_github_signature, get_raw_body


async def handle_webhook(request):
    """Handle incoming GitHub webhook with signature verification."""
    try:
        # Read raw body first for signature verification
        # This must be done before parsing JSON
        raw_body = await get_raw_body(request)
        
        # Verify webhook signature if secret is configured
        if GITHUB_WEBHOOK_SECRET:
            signature_header = request.headers.get("X-Hub-Signature-256")
            try:
                if not verify_github_signature(raw_body, signature_header, GITHUB_WEBHOOK_SECRET):
                    return web.json_response(
                        {"error": "Invalid webhook signature"},
                        status=401
                    )
            except ValueError as e:
                # Invalid signature format or missing secret
                return web.json_response(
                    {"error": f"Signature verification failed: {str(e)}"},
                    status=401
                )
        
        # Parse JSON from raw body
        data = json.loads(raw_body.decode('utf-8'))
        
        # Create event record
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": request.headers.get("X-GitHub-Event", "unknown"),
            "action": data.get("action"),
            "workflow_run": data.get("workflow_run"),
            "check_run": data.get("check_run"),
            "repository": data.get("repository", {}).get("full_name"),
            "sender": data.get("sender", {}).get("login")
        }
        
        # Load existing events
        events = []
        if EVENTS_FILE.exists():
            with open(EVENTS_FILE, 'r') as f:
                events = json.load(f)
        
        # Add new event and keep last 100
        events.append(event)
        events = events[-100:]
        
        # Save events
        with open(EVENTS_FILE, 'w') as f:
            json.dump(events, f, indent=2)
        
        return web.json_response({"status": "received"})
    except json.JSONDecodeError as e:
        return web.json_response(
            {"error": f"Invalid JSON payload: {str(e)}"},
            status=400
        )
    except Exception as e:
        return web.json_response(
            {"error": f"Internal server error: {str(e)}"},
            status=500
        )


# Create app and add route
app = web.Application()
app.router.add_post('/webhook/github', handle_webhook)


if __name__ == '__main__':
    print("🚀 Starting webhook server on http://localhost:8080")
    print("📝 Events will be saved to:", EVENTS_FILE)
    print("🔗 Webhook URL: http://localhost:8080/webhook/github")
    
    if GITHUB_WEBHOOK_SECRET:
        print("🔒 Webhook signature verification: ENABLED")
    else:
        print("⚠️  Webhook signature verification: DISABLED (set GITHUB_WEBHOOK_SECRET to enable)")
    
    web.run_app(app, host='localhost', port=8080)

