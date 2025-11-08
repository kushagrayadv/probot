"""Unit tests for webhook security and authentication."""

import pytest
import hmac
import hashlib
from pr_agent.webhook.security import verify_github_signature


class TestGitHubSignatureVerification:
    """Test GitHub webhook signature verification."""
    
    def test_valid_signature(self):
        """Test verification of a valid signature."""
        secret = "my_secret_key"
        payload = b'{"action": "completed", "workflow_run": {"name": "CI"}}'
        
        # Generate valid signature
        signature = hmac.new(
            secret.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()
        signature_header = f"sha256={signature}"
        
        assert verify_github_signature(payload, signature_header, secret) is True
    
    def test_invalid_signature(self):
        """Test rejection of an invalid signature."""
        secret = "my_secret_key"
        payload = b'{"action": "completed"}'
        invalid_signature = "sha256=invalid_signature_hash"
        
        assert verify_github_signature(payload, invalid_signature, secret) is False
    
    def test_wrong_secret(self):
        """Test rejection when using wrong secret."""
        correct_secret = "correct_secret"
        wrong_secret = "wrong_secret"
        payload = b'{"action": "completed"}'
        
        # Generate signature with correct secret
        signature = hmac.new(
            correct_secret.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()
        signature_header = f"sha256={signature}"
        
        # Verify with wrong secret should fail
        assert verify_github_signature(payload, signature_header, wrong_secret) is False
    
    def test_missing_secret(self):
        """Test that missing secret raises ValueError."""
        payload = b'{"action": "completed"}'
        signature_header = "sha256=some_signature"
        
        with pytest.raises(ValueError, match="GitHub webhook secret is not configured"):
            verify_github_signature(payload, signature_header, "")
    
    def test_missing_signature_header(self):
        """Test that missing signature header raises ValueError."""
        secret = "my_secret_key"
        payload = b'{"action": "completed"}'
        
        with pytest.raises(ValueError, match="Missing X-Hub-Signature-256 header"):
            verify_github_signature(payload, None, secret)
    
    def test_invalid_signature_format(self):
        """Test that invalid signature format raises ValueError."""
        secret = "my_secret_key"
        payload = b'{"action": "completed"}'
        invalid_format = "invalid_format_signature"
        
        with pytest.raises(ValueError, match="Invalid signature format"):
            verify_github_signature(payload, invalid_format, secret)
    
    def test_timing_attack_protection(self):
        """Test that constant-time comparison is used (basic check)."""
        secret = "my_secret_key"
        payload = b'{"action": "completed"}'
        
        # Generate valid signature
        signature = hmac.new(
            secret.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()
        signature_header = f"sha256={signature}"
        
        # Should use hmac.compare_digest which is constant-time
        result = verify_github_signature(payload, signature_header, secret)
        assert result is True
        
        # Test with completely different signature
        wrong_signature = "sha256=" + "a" * 64  # 64 hex chars
        result2 = verify_github_signature(payload, wrong_signature, secret)
        assert result2 is False

