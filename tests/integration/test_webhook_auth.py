"""Integration tests for webhook authentication."""

import pytest
import json
import hmac
import hashlib
from aiohttp.test_utils import make_mocked_request
from unittest.mock import patch
from pr_agent.webhook.server import handle_webhook
from pr_agent.config.settings import GITHUB_WEBHOOK_SECRET


class TestWebhookAuthentication:
    """Integration tests for webhook authentication."""
    
    @pytest.mark.asyncio
    async def test_webhook_with_valid_signature(self, monkeypatch):
        """Test webhook handler accepts valid signature."""
        test_secret = "test_secret_123"
        monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", test_secret)
        
        # Patch the settings module to use test secret
        from pr_agent.config import settings
        original_secret = settings.GITHUB_WEBHOOK_SECRET
        settings.GITHUB_WEBHOOK_SECRET = test_secret
        
        try:
            payload = {"action": "completed", "workflow_run": {"name": "CI"}}
            payload_bytes = json.dumps(payload).encode('utf-8')
            
            # Generate valid signature
            signature = hmac.new(
                test_secret.encode('utf-8'),
                msg=payload_bytes,
                digestmod=hashlib.sha256
            ).hexdigest()
            signature_header = f"sha256={signature}"
            
            # Create mock request
            request = make_mocked_request(
                'POST',
                '/webhook/github',
                headers={
                    'X-GitHub-Event': 'workflow_run',
                    'X-Hub-Signature-256': signature_header,
                    'Content-Type': 'application/json'
                },
                payload=payload_bytes
            )
            
            # Mock the read method
            async def mock_read():
                return payload_bytes
            request.read = mock_read
            
            response = await handle_webhook(request)
            
            assert response.status == 200
            data = json.loads(response.text)
            assert data["status"] == "received"
        finally:
            # Restore original secret
            settings.GITHUB_WEBHOOK_SECRET = original_secret
    
    @pytest.mark.asyncio
    async def test_webhook_rejects_invalid_signature(self, monkeypatch):
        """Test webhook handler rejects invalid signature."""
        test_secret = "test_secret_123"
        monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", test_secret)
        
        # Patch the settings module
        from pr_agent.config import settings
        original_secret = settings.GITHUB_WEBHOOK_SECRET
        settings.GITHUB_WEBHOOK_SECRET = test_secret
        
        try:
            payload = {"action": "completed"}
            payload_bytes = json.dumps(payload).encode('utf-8')
            invalid_signature = "sha256=invalid_signature_hash"
            
            request = make_mocked_request(
                'POST',
                '/webhook/github',
                headers={
                    'X-GitHub-Event': 'workflow_run',
                    'X-Hub-Signature-256': invalid_signature,
                    'Content-Type': 'application/json'
                },
                payload=payload_bytes
            )
            
            async def mock_read():
                return payload_bytes
            request.read = mock_read
            
            response = await handle_webhook(request)
            
            assert response.status == 401
            data = json.loads(response.text)
            assert "error" in data
            assert "Invalid webhook signature" in data["error"]
        finally:
            settings.GITHUB_WEBHOOK_SECRET = original_secret
    
    @pytest.mark.asyncio
    async def test_webhook_without_secret_allows_all(self, monkeypatch):
        """Test webhook allows requests when secret is not configured."""
        monkeypatch.delenv("GITHUB_WEBHOOK_SECRET", raising=False)
        
        # Patch the settings module
        from pr_agent.config import settings
        original_secret = settings.GITHUB_WEBHOOK_SECRET
        settings.GITHUB_WEBHOOK_SECRET = ""
        
        try:
            payload = {"action": "completed"}
            payload_bytes = json.dumps(payload).encode('utf-8')
            
            request = make_mocked_request(
                'POST',
                '/webhook/github',
                headers={
                    'X-GitHub-Event': 'workflow_run',
                    'Content-Type': 'application/json'
                },
                payload=payload_bytes
            )
            
            async def mock_read():
                return payload_bytes
            request.read = mock_read
            
            response = await handle_webhook(request)
            
            # Should accept when no secret is configured (backward compatibility)
            assert response.status == 200
        finally:
            settings.GITHUB_WEBHOOK_SECRET = original_secret
    
    @pytest.mark.asyncio
    async def test_webhook_rejects_missing_signature_when_secret_set(self, monkeypatch):
        """Test webhook rejects requests without signature when secret is configured."""
        test_secret = "test_secret_123"
        monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", test_secret)
        
        # Patch the settings module
        from pr_agent.config import settings
        original_secret = settings.GITHUB_WEBHOOK_SECRET
        settings.GITHUB_WEBHOOK_SECRET = test_secret
        
        try:
            payload = {"action": "completed"}
            payload_bytes = json.dumps(payload).encode('utf-8')
            
            request = make_mocked_request(
                'POST',
                '/webhook/github',
                headers={
                    'X-GitHub-Event': 'workflow_run',
                    'Content-Type': 'application/json'
                },
                payload=payload_bytes
            )
            
            async def mock_read():
                return payload_bytes
            request.read = mock_read
            
            response = await handle_webhook(request)
            
            assert response.status == 401
            data = json.loads(response.text)
            assert "error" in data
            assert "Signature verification failed" in data["error"]
        finally:
            settings.GITHUB_WEBHOOK_SECRET = original_secret

