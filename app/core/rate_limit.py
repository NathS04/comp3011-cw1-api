import time
from fastapi import Request, Response
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, requests_per_minute: int = 120):
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # seconds
        # Dictionary to store request timestamps per IP + path key
        # Structure: { "ip:path_key": [timestamp1, timestamp2, ...] }
        self.history = defaultdict(list)

    def is_allowed(self, client_ip: str, path_key: str) -> bool:
        now = time.time()
        key = f"{client_ip}:{path_key}"
        
        # Clean up old timestamps
        self.history[key] = [t for t in self.history[key] if now - t < self.window_size]
        
        if len(self.history[key]) >= self.requests_per_minute:
            return False
            
        self.history[key].append(now)
        return True

# Global limiters
global_limiter = RateLimiter(requests_per_minute=120)
auth_limiter = RateLimiter(requests_per_minute=10) # Stricter for login
