"""Vercel serverless function entry point for FastAPI application."""

import sys
from pathlib import Path

# Add the demo/backend to the Python path
backend_path = Path(__file__).parent.parent / "demo" / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    from src.main import app as fastapi_app
except Exception as e:
    import traceback
    print(f"[ERROR] Failed to import FastAPI app: {e}")
    traceback.print_exc()
    
    from fastapi import FastAPI
    fastapi_app = FastAPI()
    
    @fastapi_app.get("/health")
    async def health():
        return {"status": "error", "detail": str(e)}

# Export the ASGI app for Vercel
app = fastapi_app

__all__ = ["app"]
