from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self, requests_per_second: int = 10):
        self.requests_per_second = requests_per_second
        self.requests: Dict[str, list] = {}
    
    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # 현재 IP의 요청 기록 정리
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < 1.0
            ]
        else:
            self.requests[client_ip] = []
            
        # 요청 수 체크
        if len(self.requests[client_ip]) >= self.requests_per_second:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"}
            )
            
        self.requests[client_ip].append(current_time)
        response = await call_next(request)
        return response 