from typing import Optional, Dict, Any
import aiohttp
import asyncio

from pr_agent.utils.logger import get_logger

logger = get_logger(__name__)


class HTTPClient:
    """Async HTTP client with common patterns and error handling."""
    
    def __init__(self, timeout: float = 10.0, default_headers: Optional[Dict[str, str]] = None):
        """Initialize HTTP client.
        
        Args:
            timeout: Default timeout in seconds (default: 10.0)
            default_headers: Default headers to include in all requests
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.default_headers = default_headers or {}
    
    async def post_json(
        self,
        url: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> tuple[int, str]:
        """Send a POST request with JSON data.
        
        Args:
            url: Target URL
            data: JSON data to send
            headers: Optional additional headers
            timeout: Optional timeout override
            
        Returns:
            Tuple of (status_code, response_text)
            
        Raises:
            asyncio.TimeoutError: If request times out
            aiohttp.ClientError: If connection error occurs
        """
        request_headers = {**self.default_headers, "Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        
        request_timeout = aiohttp.ClientTimeout(total=timeout) if timeout else self.timeout
        
        async with aiohttp.ClientSession(timeout=request_timeout) as session:
            async with session.post(url, json=data, headers=request_headers) as response:
                response_text = await response.text()
                return response.status, response_text
    
    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> tuple[int, str]:
        """Send a GET request.
        
        Args:
            url: Target URL
            headers: Optional additional headers
            timeout: Optional timeout override
            
        Returns:
            Tuple of (status_code, response_text)
            
        Raises:
            asyncio.TimeoutError: If request times out
            aiohttp.ClientError: If connection error occurs
        """
        request_headers = {**self.default_headers}
        if headers:
            request_headers.update(headers)
        
        request_timeout = aiohttp.ClientTimeout(total=timeout) if timeout else self.timeout
        
        async with aiohttp.ClientSession(timeout=request_timeout) as session:
            async with session.get(url, headers=request_headers) as response:
                response_text = await response.text()
                return response.status, response_text


# Default HTTP client instance
default_client = HTTPClient(timeout=10.0)

