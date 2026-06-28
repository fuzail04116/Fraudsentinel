import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.monitoring.metrics_exporter import REQUEST_LATENCY

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        if request.url.path == "/predict" and request.method == "POST":
            REQUEST_LATENCY.observe(process_time)
            
        return response
