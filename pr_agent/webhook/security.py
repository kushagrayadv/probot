"""Webhook security and authentication utilities."""

import hmac
import hashlib
from typing import Optional


def verify_github_signature(
    payload_body: bytes,
    signature_header: Optional[str],
    secret: str
) -> bool:
    """Verify GitHub webhook signature using HMAC SHA256.
    
    GitHub sends webhook signatures in the X-Hub-Signature-256 header
    in the format: sha256=<hex_digest>
    
    Args:
        payload_body: Raw request body as bytes
        signature_header: Value from X-Hub-Signature-256 header
        secret: GitHub webhook secret configured in repository settings
        
    Returns:
        True if signature is valid, False otherwise
        
    Raises:
        ValueError: If secret is empty or signature header is missing
    """
    if not secret:
        raise ValueError("GitHub webhook secret is not configured")
    
    if not signature_header:
        raise ValueError("Missing X-Hub-Signature-256 header")
    
    # GitHub sends signature as "sha256=<hex_digest>"
    if not signature_header.startswith("sha256="):
        raise ValueError("Invalid signature format. Expected 'sha256=<hex_digest>'")
    
    # Extract the hex digest
    received_signature = signature_header[7:]  # Remove "sha256=" prefix
    
    # Compute expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, received_signature)


async def get_raw_body(request) -> bytes:
    """Read raw request body for signature verification.
    
    This must be called before request.json() to preserve the body.
    In aiohttp, reading the body consumes it, so we read it once here
    and then parse JSON from the bytes.
    
    Args:
        request: aiohttp request object
        
    Returns:
        Raw request body as bytes
    """
    return await request.read()

