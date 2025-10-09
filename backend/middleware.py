import time
import hashlib
from typing import Dict, List, Optional
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent API abuse
    """
    
    def __init__(self, app, calls: int = 10, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Number of calls allowed
        self.period = period  # Time period in seconds
        self.clients: Dict[str, List[float]] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address)
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if self._is_rate_limited(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.calls} requests per {self.period} seconds allowed",
                    "retry_after": self.period
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self._get_remaining_calls(client_ip)
        reset_time = self._get_reset_time(client_ip)
        
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded headers (reverse proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited"""
        current_time = time.time()
        
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        
        # Clean old entries
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if current_time - timestamp < self.period
        ]
        
        # Check if limit exceeded
        if len(self.clients[client_ip]) >= self.calls:
            return True
        
        # Add current request
        self.clients[client_ip].append(current_time)
        return False
    
    def _get_remaining_calls(self, client_ip: str) -> int:
        """Get remaining calls for client"""
        if client_ip not in self.clients:
            return self.calls
        
        current_time = time.time()
        valid_calls = [
            timestamp for timestamp in self.clients[client_ip]
            if current_time - timestamp < self.period
        ]
        
        return max(0, self.calls - len(valid_calls))
    
    def _get_reset_time(self, client_ip: str) -> int:
        """Get reset time for rate limit"""
        if client_ip not in self.clients or not self.clients[client_ip]:
            return int(time.time() + self.period)
        
        oldest_call = min(self.clients[client_ip])
        return int(oldest_call + self.period)

class ContentValidationMiddleware(BaseHTTPMiddleware):
    """
    Content validation middleware for uploaded files
    """
    
    ALLOWED_MIME_TYPES = {
        'image/jpeg',
        'image/jpg', 
        'image/png',
        'image/webp',
        'image/bmp'
    }
    
    SUSPICIOUS_PATTERNS = [
        b'<script',
        b'javascript:',
        b'<iframe',
        b'<object',
        b'<embed'
    ]
    
    MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB
    
    async def dispatch(self, request: Request, call_next):
        # Only validate file uploads
        if request.url.path in ['/process', '/batch-process'] and request.method == 'POST':
            try:
                await self._validate_request(request)
            except Exception as e:
                logger.error(f"Content validation failed: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Content validation failed",
                        "message": str(e)
                    }
                )
        
        response = await call_next(request)
        return response
    
    async def _validate_request(self, request: Request):
        """Validate uploaded content"""
        # Note: This is a simplified validation
        # In practice, you'd need to parse multipart data more carefully
        
        content_type = request.headers.get('content-type', '')
        
        if not content_type.startswith('multipart/form-data'):
            return  # Not a file upload
        
        # Basic content length check
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.MAX_FILE_SIZE:
            raise ValueError(f"File too large. Maximum {self.MAX_FILE_SIZE} bytes allowed.")

class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    API Key authentication middleware (optional)
    """
    
    def __init__(self, app, require_api_key: bool = False, valid_keys: Optional[List[str]] = None):
        super().__init__(app)
        self.require_api_key = require_api_key
        self.valid_keys = set(valid_keys or [])
        
        # Add a default development key if none provided
        if not self.valid_keys and require_api_key:
            self.valid_keys.add("dev-key-12345")
            logger.warning("Using default development API key. Change this in production!")
    
    async def dispatch(self, request: Request, call_next):
        if not self.require_api_key:
            return await call_next(request)
        
        # Skip API key for health checks
        if request.url.path in ['/health', '/', '/docs', '/redoc', '/openapi.json']:
            return await call_next(request)
        
        # Check API key
        api_key = self._extract_api_key(request)
        
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "API key required",
                    "message": "Please provide a valid API key in headers or query parameters"
                }
            )
        
        if api_key not in self.valid_keys:
            logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Invalid API key",
                    "message": "The provided API key is not valid"
                }
            )
        
        # Add API key to request state for logging
        request.state.api_key = api_key
        
        response = await call_next(request)
        return response
    
    def _extract_api_key(self, request: Request) -> Optional[str]:
        """Extract API key from request headers or query parameters"""
        # Check Authorization header
        auth_header = request.headers.get('authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Check X-API-Key header
        api_key_header = request.headers.get('x-api-key')
        if api_key_header:
            return api_key_header
        
        # Check query parameter
        return request.query_params.get('api_key')

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to responses
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # Add HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

def validate_image_content(file_content: bytes, filename: str) -> bool:
    """
    Validate image file content for security
    
    Args:
        file_content: Raw file bytes
        filename: Original filename
    
    Returns:
        True if content is safe, False otherwise
    """
    try:
        # Check file signature (magic numbers)
        if not _is_valid_image_signature(file_content):
            return False
        
        # Check for suspicious patterns
        content_lower = file_content.lower()
        for pattern in ContentValidationMiddleware.SUSPICIOUS_PATTERNS:
            if pattern in content_lower:
                logger.warning(f"Suspicious content detected in {filename}")
                return False
        
        # Additional checks could include:
        # - EXIF data validation
        # - Image dimension limits
        # - Pixel content analysis
        
        return True
        
    except Exception as e:
        logger.error(f"Content validation error for {filename}: {str(e)}")
        return False

def _is_valid_image_signature(content: bytes) -> bool:
    """Check if file has valid image signature"""
    if len(content) < 8:
        return False
    
    # JPEG signatures
    if content.startswith(b'\xff\xd8\xff'):
        return True
    
    # PNG signature
    if content.startswith(b'\x89PNG\r\n\x1a\n'):
        return True
    
    # WebP signature
    if content.startswith(b'RIFF') and b'WEBP' in content[:12]:
        return True
    
    # BMP signature
    if content.startswith(b'BM'):
        return True
    
    # GIF signature
    if content.startswith(b'GIF87a') or content.startswith(b'GIF89a'):
        return True
    
    return False

def get_content_hash(content: bytes) -> str:
    """Generate content hash for caching/deduplication"""
    return hashlib.sha256(content).hexdigest()

# Usage in main.py:
"""
from middleware import (
    RateLimitMiddleware, 
    ContentValidationMiddleware, 
    APIKeyMiddleware,
    SecurityHeadersMiddleware
)

# Add to your FastAPI app
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, calls=10, period=60)
app.add_middleware(ContentValidationMiddleware)
# app.add_middleware(APIKeyMiddleware, require_api_key=True, valid_keys=["your-api-key"])
"""